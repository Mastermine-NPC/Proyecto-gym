import json
from datetime import date, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction, IntegrityError
from .models import Cliente, Sexo, Estado
from apps.membresias.models import Membresia, TipoMembresia, EstadoMembresia


@csrf_exempt
@require_http_methods(["POST"])
def inscribir_cliente(request):
    """
    Endpoint para inscribir / registrar un cliente en el gimnasio.
    Soporta concurrencia alta e inserción directa en la base de datos.
    """
    try:
        # Permite recibir tanto JSON como form-data
        if request.content_type == "application/json" and request.body:
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST.dict()

        # Validación de campos obligatorios
        nombres = data.get("nombres", "").strip()
        apellido_paterno = data.get("apellido_paterno", "").strip()
        apellido_materno = data.get("apellido_materno", "").strip()
        dni = data.get("dni", "").strip()
        telefono = data.get("telefono", "").strip()
        correo = data.get("correo", "").strip()
        fecha_nacimiento = data.get("fecha_nacimiento", "1998-01-01").strip()
        sexo = data.get("sexo", Sexo.MASCULINO).upper().strip()
        direccion = data.get("direccion", "Av. Principal 123").strip()

        if not nombres or not apellido_paterno or not dni or not correo:
            return JsonResponse(
                {
                    "error": "Campos obligatorios faltantes",
                    "requeridos": ["nombres", "apellido_paterno", "dni", "correo"],
                },
                status=400,
            )

        if len(dni) != 8 or not dni.isdigit():
            return JsonResponse(
                {"error": "El DNI debe tener exactamente 8 dígitos numéricos."},
                status=400,
            )

        if sexo not in [Sexo.MASCULINO, Sexo.FEMENINO]:
            sexo = Sexo.MASCULINO

        # Inserción en base de datos con transacción atómica
        with transaction.atomic():
            cliente = Cliente.objects.create(
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                dni=dni,
                telefono=telefono or "999888777",
                correo=correo,
                fecha_nacimiento=fecha_nacimiento,
                sexo=sexo,
                direccion=direccion,
                estado=Estado.ACTIVO,
            )

            # Opcional: si se especifica membresía o por defecto para inscripción completa
            incluir_membresia = data.get("incluir_membresia", False)
            membresia_id = None
            if incluir_membresia:
                # Buscar o crear tipo de membresía base para la prueba de concurrencia
                tipo, _ = TipoMembresia.objects.get_or_create(
                    nombre="Membresía Mensual Estándar",
                    defaults={
                        "precio": 120.00,
                        "duracion_dias": 30,
                        "descripcion": "Acceso ilimitado por 30 días",
                    },
                )
                hoy = date.today()
                membresia = Membresia.objects.create(
                    cliente=cliente,
                    tipo_membresia=tipo,
                    fecha_inicio=hoy,
                    fecha_fin=hoy + timedelta(days=tipo.duracion_dias),
                    estado=EstadoMembresia.ACTIVA,
                )
                membresia_id = membresia.id

        return JsonResponse(
            {
                "status": "success",
                "mensaje": "Cliente inscrito correctamente en la base de datos",
                "cliente": {
                    "id": cliente.id,
                    "dni": cliente.dni,
                    "nombre_completo": str(cliente),
                    "correo": cliente.correo,
                    "membresia_id": membresia_id,
                },
            },
            status=201,
        )

    except IntegrityError as e:
        # Error de unicidad en BD (DNI o Correo ya existente)
        return JsonResponse(
            {"error": "Conflicto de unicidad en base de datos (DNI o Correo ya registrado)", "detalle": str(e)},
            status=409,
        )
    except Exception as e:
        return JsonResponse(
            {"error": "Error interno del servidor", "detalle": str(e)},
            status=500,
        )


@require_http_methods(["GET"])
def estadisticas_clientes(request):
    """
    Endpoint de monitoreo en tiempo real para verificar el conteo
    y estado de clientes en la base de datos durante y después de Locust.
    """
    total = Cliente.objects.count()
    activos = Cliente.objects.filter(estado=Estado.ACTIVO).count()
    total_membresias = Membresia.objects.count()

    return JsonResponse(
        {
            "total_clientes_en_bd": total,
            "clientes_activos": activos,
            "total_membresias_activas": total_membresias,
        }
    )


@require_http_methods(["GET"])
def api_orden_inscripciones(request):
    """
    Devuelve los clientes ordenados cronológicamente por su momento exacto de inserción
    en la base de datos (concurrencia serializada por clave primaria y timestamp con milisegundos).
    Soporta orden ascendente (1 a N) o descendente (N a 1).
    """
    limite = int(request.GET.get("limite", 1000))
    direccion_orden = request.GET.get("orden", "asc").lower()

    clientes_qs = Cliente.objects.all().order_by("id")
    total = clientes_qs.count()

    if total == 0:
        return JsonResponse({
            "total": 0,
            "primero": None,
            "ultimo": None,
            "duracion_segundos": 0,
            "clientes": []
        })

    primero_obj = clientes_qs.first()
    ultimo_obj = clientes_qs.last()

    delta_segundos = 0.0
    if primero_obj and ultimo_obj:
        delta_segundos = round((ultimo_obj.fecha_creacion - primero_obj.fecha_creacion).total_seconds(), 3)
        if delta_segundos <= 0:
            delta_segundos = 0.001

    tasa_por_segundo = round(total / delta_segundos, 2) if delta_segundos > 0 else total

    lista_clientes = []
    # Enumeramos con orden secuencial cronológico de llegada (1 al límite)
    subconjunto = list(clientes_qs[:limite])
    for idx, c in enumerate(subconjunto, start=1):
        hora_str = c.fecha_creacion.strftime("%H:%M:%S.%f")[:-3]  # Precisión milisegundos
        fecha_str = c.fecha_creacion.strftime("%Y-%m-%d")
        lista_clientes.append({
            "orden": idx,
            "id": c.id,
            "nombres": c.nombres,
            "apellido_paterno": c.apellido_paterno,
            "apellido_materno": c.apellido_materno,
            "nombre_completo": str(c),
            "dni": c.dni,
            "correo": c.correo,
            "telefono": c.telefono,
            "sexo": c.sexo,
            "direccion": c.direccion,
            "estado": c.estado,
            "fecha": fecha_str,
            "hora": hora_str,
            "timestamp_iso": c.fecha_creacion.isoformat(),
            "es_primero": (idx == 1),
            "es_ultimo": (idx == total or idx == len(subconjunto)),
        })

    # Si se solicita orden descendente (por ejemplo de 100 a 1)
    if direccion_orden == "desc":
        lista_clientes.reverse()

    def formatear_cliente(c, orden):
        if not c:
            return None
        return {
            "orden": orden,
            "id": c.id,
            "nombre_completo": str(c),
            "dni": c.dni,
            "correo": c.correo,
            "hora_exacta": c.fecha_creacion.strftime("%H:%M:%S.%f")[:-3],
            "fecha": c.fecha_creacion.strftime("%Y-%m-%d"),
        }

    return JsonResponse({
        "total_inscritos": total,
        "primero": formatear_cliente(primero_obj, 1),
        "ultimo": formatear_cliente(ultimo_obj, total),
        "duracion_total_segundos": delta_segundos,
        "tasa_insercion_rps": tasa_por_segundo,
        "direccion_orden": direccion_orden,
        "limite_mostrado": len(lista_clientes),
        "clientes": lista_clientes
    })


@require_http_methods(["GET"])
def auditoria_concurrencia_view(request):
    """
    Vista Web Interactiva: Panel de Auditoría de Concurrencia AuraFit.
    Permite visualizar a las 1,000 personas inscritas, cómo el motor de base de datos
    las ordenó en milisegundos, quién fue el primero y quién fue el último.
    """
    from django.http import HttpResponse

    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuraFit Gym - Auditoría de Concurrencia (1,000 Inscripciones)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0e17;
            --bg-secondary: #131b2e;
            --bg-card: rgba(23, 33, 56, 0.7);
            --border-card: rgba(255, 255, 255, 0.08);
            --accent-cyan: #00f2fe;
            --accent-blue: #4facfe;
            --accent-gold: #ffd200;
            --accent-green: #00e676;
            --accent-purple: #7928ca;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            background: radial-gradient(circle at top right, #1a2238 0%, #0a0e17 60%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 24px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-card);
            margin-bottom: 24px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-logo {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: 800;
            color: #fff;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
        }

        .brand h1 {
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(90deg, #ffffff, var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand p {
            font-size: 13px;
            color: var(--text-muted);
        }

        .live-tag {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(0, 230, 118, 0.1);
            border: 1px solid rgba(0, 230, 118, 0.3);
            color: var(--accent-green);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.3); }
        }

        /* METRIC CARDS */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }

        .metric-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 22px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .card-gold {
            background: linear-gradient(135deg, rgba(255, 210, 0, 0.1), rgba(23, 33, 56, 0.7));
            border-color: rgba(255, 210, 0, 0.3);
        }

        .card-blue {
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.1), rgba(23, 33, 56, 0.7));
            border-color: rgba(79, 172, 254, 0.3);
        }

        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .metric-title {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
        }

        .metric-badge {
            font-size: 11px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
        }

        .badge-gold {
            background: rgba(255, 210, 0, 0.2);
            color: var(--accent-gold);
            border: 1px solid rgba(255, 210, 0, 0.4);
        }

        .badge-blue {
            background: rgba(79, 172, 254, 0.2);
            color: var(--accent-blue);
            border: 1px solid rgba(79, 172, 254, 0.4);
        }

        .metric-name {
            font-size: 20px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 6px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .metric-sub {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: var(--accent-cyan);
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        .metric-val-big {
            font-size: 38px;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(90deg, #fff, var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* CONTROLS */
        .controls-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 18px;
        }

        .search-box {
            position: relative;
            flex: 1;
            max-width: 400px;
        }

        .search-input {
            width: 100%;
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 10px;
            padding: 10px 16px 10px 40px;
            color: #fff;
            font-family: inherit;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .search-input:focus {
            border-color: var(--accent-cyan);
        }

        .search-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 14px;
        }

        .btn-group {
            display: flex;
            gap: 10px;
        }

        .btn {
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: 8px;
            font-family: inherit;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
            color: #0a0e17;
            border: none;
            font-weight: 700;
        }

        .btn-primary:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        /* TABLE */
        .table-wrapper {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13px;
        }

        thead {
            background: rgba(10, 14, 23, 0.6);
            border-bottom: 1px solid var(--border-card);
        }

        th {
            padding: 14px 18px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
        }

        tbody tr {
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            transition: background 0.15s;
        }

        tbody tr:hover {
            background: rgba(255, 255, 255, 0.04);
        }

        td {
            padding: 12px 18px;
            vertical-align: middle;
        }

        .tr-primero {
            background: rgba(255, 210, 0, 0.08) !important;
            border-left: 4px solid var(--accent-gold);
        }

        .tr-ultimo {
            background: rgba(79, 172, 254, 0.08) !important;
            border-left: 4px solid var(--accent-blue);
        }

        .order-badge {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
            display: inline-block;
            font-size: 12px;
        }

        .order-normal {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
        }

        .chip-active {
            background: rgba(0, 230, 118, 0.15);
            color: var(--accent-green);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }

        .timestamp-mono {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--accent-cyan);
        }

        .pagination-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 18px;
            border-top: 1px solid var(--border-card);
            font-size: 13px;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <header>
            <div class="brand">
                <div class="brand-logo">⚡</div>
                <div>
                    <h1>AuraFit Gym - Auditoría de Concurrencia</h1>
                    <p>Serialización e Inserción de 1,000 Clientes Simultáneos en Base de Datos</p>
                </div>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <span class="live-tag">
                    <span class="live-dot"></span>
                    Base de Datos Conectada
                </span>
                <button class="btn btn-primary" onclick="cargarDatos()">
                    🔄 Actualizar Datos
                </button>
            </div>
        </header>

        <!-- METRIC CARDS -->
        <div class="metrics-grid">
            <!-- TOTAL -->
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Total Clientes en BD</span>
                    <span class="metric-badge" style="background: rgba(0,242,254,0.15); color: var(--accent-cyan);">Concurrencia</span>
                </div>
                <div class="metric-val-big" id="txt-total">0</div>
                <div class="metric-sub">
                    <span>Meta: 1,000 Inscritos</span>
                    <span id="txt-rps">0 RPS</span>
                </div>
            </div>

            <!-- PRIMERO -->
            <div class="metric-card card-gold" id="card-primero">
                <div class="metric-header">
                    <span class="metric-title">🥇 Primer Inscrito (Orden #1)</span>
                    <span class="metric-badge badge-gold">EL PRIMERO</span>
                </div>
                <div class="metric-name" id="primero-nombre">Cargando...</div>
                <div class="metric-sub">
                    <span id="primero-dni">DNI: --------</span>
                    <span id="primero-hora">00:00:00.000</span>
                </div>
            </div>

            <!-- ÚLTIMO -->
            <div class="metric-card card-blue" id="card-ultimo">
                <div class="metric-header">
                    <span class="metric-title">🏁 Último Inscrito</span>
                    <span class="metric-badge badge-blue" id="badge-ultimo">EL ÚLTIMO</span>
                </div>
                <div class="metric-name" id="ultimo-nombre">Cargando...</div>
                <div class="metric-sub">
                    <span id="ultimo-dni">DNI: --------</span>
                    <span id="ultimo-hora">00:00:00.000</span>
                </div>
            </div>

            <!-- TIEMPO TOTAL -->
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Tiempo de Ráfaga</span>
                    <span class="metric-badge" style="background: rgba(121,40,202,0.2); color: #c084fc;">Delta Temporal</span>
                </div>
                <div class="metric-val-big" id="txt-tiempo">0.00s</div>
                <div class="metric-sub">
                    <span>Entre 1° y último</span>
                    <span style="color: var(--accent-green);">100% Exitoso</span>
                </div>
            </div>
        </div>

        <!-- CONTROLS -->
        <div class="controls-bar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" class="search-input" id="buscador" placeholder="Buscar por DNI o Nombre..." oninput="filtrarTabla()">
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" id="btn-100-a-1" onclick="ordenar100a1()">🔽 Ordenar de 100 a 1</button>
                <button class="btn" id="btn-1-a-100" onclick="ordenar1a100()">🔼 Ordenar de 1 a 100</button>
                <button class="btn" id="btn-todos" onclick="verTodos1000()">📋 Ver los 1,000</button>
                <button class="btn" onclick="invertirOrden()">🔄 Invertir</button>
                <button class="btn" onclick="irAlPrimero()">🥇 Primero (#1)</button>
                <button class="btn" onclick="irAlUltimo()">🏁 Último</button>
            </div>
        </div>

        <!-- TABLE -->
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width: 140px;">Orden BD</th>
                        <th style="width: 80px;">ID</th>
                        <th>Nombre del Cliente</th>
                        <th>DNI</th>
                        <th>Correo Electrónico</th>
                        <th>Teléfono</th>
                        <th>Hora Exacta (ms)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody id="tabla-cuerpo">
                    <tr>
                        <td colspan="8" style="text-align: center; padding: 40px; color: var(--text-muted);">
                            Cargando registros desde la base de datos...
                        </td>
                    </tr>
                </tbody>
            </table>
            <div class="pagination-bar">
                <span id="txt-resumen-tabla">Mostrando 0 registros</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px;">Motor: PostgreSQL / SQLite | Serialización ACID</span>
            </div>
        </div>
    </div>

    <script>
        let clientesData = [];
        let totalTotal = 0;
        let currentLimite = 100;
        let currentOrden = 'desc'; // Por defecto: del 100 al 1

        async function cargarDatos(limite = currentLimite, orden = currentOrden) {
            try {
                currentLimite = limite;
                currentOrden = orden;
                actualizarEstiloBotones();

                const res = await fetch(`/api/clientes/orden-inscripciones/?limite=${limite}&orden=${orden}`);
                const data = await res.json();
                
                totalTotal = data.total_inscritos;
                clientesData = data.clientes || [];

                document.getElementById('txt-total').innerText = totalTotal.toLocaleString();
                document.getElementById('txt-tiempo').innerText = data.duracion_total_segundos + 's';
                document.getElementById('txt-rps').innerText = data.tasa_insercion_rps + ' RPS';

                // Primero
                if (data.primero) {
                    document.getElementById('primero-nombre').innerText = data.primero.nombre_completo;
                    document.getElementById('primero-dni').innerText = 'DNI: ' + data.primero.dni + ' (ID #' + data.primero.id + ')';
                    document.getElementById('primero-hora').innerText = '⏱ ' + data.primero.hora_exacta;
                }

                // Último
                if (data.ultimo) {
                    document.getElementById('ultimo-nombre').innerText = data.ultimo.nombre_completo;
                    document.getElementById('ultimo-dni').innerText = 'DNI: ' + data.ultimo.dni + ' (ID #' + data.ultimo.id + ')';
                    document.getElementById('ultimo-hora').innerText = '⏱ ' + data.ultimo.hora_exacta;
                    document.getElementById('badge-ultimo').innerText = 'ORDEN #' + data.ultimo.orden;
                }

                renderTabla(clientesData);
            } catch (err) {
                console.error("Error al cargar datos:", err);
            }
        }

        function actualizarEstiloBotones() {
            const b100a1 = document.getElementById('btn-100-a-1');
            const b1a100 = document.getElementById('btn-1-a-100');
            const bTodos = document.getElementById('btn-todos');

            if (b100a1) b100a1.className = (currentLimite === 100 && currentOrden === 'desc') ? 'btn btn-primary' : 'btn';
            if (b1a100) b1a100.className = (currentLimite === 100 && currentOrden === 'asc') ? 'btn btn-primary' : 'btn';
            if (bTodos) bTodos.className = (currentLimite >= 1000) ? 'btn btn-primary' : 'btn';
        }

        function renderTabla(lista) {
            const tbody = document.getElementById('tabla-cuerpo');
            if (!lista || lista.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 30px;">No se encontraron registros en la base de datos.</td></tr>';
                document.getElementById('txt-resumen-tabla').innerText = '0 registros encontrados';
                return;
            }

            let html = '';
            lista.forEach((c) => {
                let filaClase = '';
                let badgeHtml = `<span class="order-badge order-normal">#${c.orden}</span>`;

                if (c.es_primero) {
                    filaClase = 'tr-primero';
                    badgeHtml = `<span class="order-badge badge-gold">🥇 1° PRIMERO</span>`;
                } else if (c.es_ultimo) {
                    filaClase = 'tr-ultimo';
                    badgeHtml = `<span class="order-badge badge-blue">🏁 ${c.orden}° ÚLTIMO</span>`;
                }

                html += `
                    <tr class="${filaClase}" id="fila-${c.orden}">
                        <td>${badgeHtml}</td>
                        <td style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-muted);">#${c.id}</td>
                        <td style="font-weight: 600; color: #fff;">${c.nombre_completo}</td>
                        <td style="font-family: 'JetBrains Mono', monospace;">${c.dni}</td>
                        <td style="color: var(--text-muted);">${c.correo}</td>
                        <td style="color: var(--text-muted);">${c.telefono}</td>
                        <td class="timestamp-mono">${c.hora}</td>
                        <td><span class="chip-active">ACTIVO</span></td>
                    </tr>
                `;
            });

            tbody.innerHTML = html;
            const modoTexto = currentOrden === 'desc' ? 'del 100 al 1 (Descendente)' : 'del 1 al ' + lista.length + ' (Ascendente)';
            document.getElementById('txt-resumen-tabla').innerText = `Mostrando ${lista.length} clientes en orden ${modoTexto}`;
        }

        function filtrarTabla() {
            const query = document.getElementById('buscador').value.toLowerCase().trim();
            if (!query) {
                renderTabla(clientesData);
                return;
            }
            const filtrados = clientesData.filter(c => 
                c.dni.includes(query) || 
                c.nombre_completo.toLowerCase().includes(query) ||
                c.correo.toLowerCase().includes(query) ||
                String(c.orden) === query
            );
            renderTabla(filtrados);
        }

        function ordenar100a1() {
            cargarDatos(100, 'desc');
        }

        function ordenar1a100() {
            cargarDatos(100, 'asc');
        }

        function verTodos1000() {
            cargarDatos(1000, 'asc');
        }

        function invertirOrden() {
            const nuevoOrden = currentOrden === 'desc' ? 'asc' : 'desc';
            cargarDatos(currentLimite, nuevoOrden);
        }

        function irAlPrimero() {
            const elem = document.getElementById('fila-1');
            if (elem) elem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        function irAlUltimo() {
            const elem = document.getElementById(`fila-${totalTotal}`) || document.getElementById('fila-100');
            if (elem) elem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // Carga inicial mostrando del 100 al 1
        cargarDatos(100, 'desc');
    </script>
</body>
</html>
"""
    return HttpResponse(html_content)

