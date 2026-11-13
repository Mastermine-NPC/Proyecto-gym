import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from apps.clientes.models import Cliente, Sexo, Estado
from apps.membresias.models import Membresia


class ClientesMasivoAPITestCase(TestCase):
    """
    Suite exhaustiva de 500 pruebas automatizadas para el módulo de Clientes,
    Membresías, API de concurrencia y validaciones de borde.
    """

    def setUp(self):
        self.client = Client()
        self.url_inscribir = reverse("clientes:inscribir_cliente")
        self.url_estadisticas = reverse("clientes:estadisticas_clientes")
        self.url_orden = reverse("clientes:api_orden_inscripciones")
        self.url_auditoria = reverse("auditoria")


# ============================================================================
# 1. GENERACIÓN DE 300 PRUEBAS DE INSCRIPCIÓN VÁLIDA (JSON Y FORM-DATA)
# ============================================================================
def _make_valid_registration_test(idx):
    def _test(self):
        dni = f"{10000000 + idx:08d}"
        incluir_mem = (idx % 2 == 0)
        sexo = "M" if idx % 3 != 0 else "F"
        payload = {
            "nombres": f"ClientePrueba{idx}",
            "apellido_paterno": f"Paterno{idx}",
            "apellido_materno": f"Materno{idx}" if idx % 4 != 0 else "",
            "dni": dni,
            "telefono": f"9{10000000 + idx:08d}",
            "correo": f"cliente{idx}@aurafit.pe",
            "fecha_nacimiento": f"{1980 + (idx % 25)}-{(idx % 12) + 1:02d}-{(idx % 28) + 1:02d}",
            "sexo": sexo,
            "direccion": f"Av. Prueba {idx}",
            "incluir_membresia": incluir_mem,
        }
        response = self.client.post(
            self.url_inscribir,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["cliente"]["dni"], dni)
        if incluir_mem:
            self.assertIsNotNone(data["cliente"]["membresia_id"])
        else:
            self.assertIsNone(data["cliente"]["membresia_id"])

    return _test


for _i in range(1, 301):
    setattr(
        ClientesMasivoAPITestCase,
        f"test_01_inscripcion_valida_{_i:03d}",
        _make_valid_registration_test(_i),
    )


# ============================================================================
# 2. GENERACIÓN DE 100 PRUEBAS DE ENTRADAS INVÁLIDAS Y CASOS DE BORDE
# ============================================================================
INVALID_CASES = []

# 2.1: 40 casos de DNI inválido (longitudes erróneas, letras, símbolos, vacío)
for _i in range(1, 41):
    if _i <= 10:
        bad_dni = str(10 ** (_i % 7))  # Menos de 8 dígitos
    elif _i <= 20:
        bad_dni = f"1234567{chr(64 + (_i - 10))}"  # Contiene letra
    elif _i <= 30:
        bad_dni = f"{100000000 + _i}"  # 9 dígitos
    else:
        bad_dni = f"123-45{_i:02d}"  # Guiones / símbolos
    INVALID_CASES.append((
        f"dni_invalido_{_i:02d}",
        {
            "nombres": "Usuario",
            "apellido_paterno": "Prueba",
            "dni": bad_dni,
            "correo": f"user_dni_{_i}@aurafit.pe",
        },
        400,
    ))

# 2.2: 20 casos de campos obligatorios faltantes o vacíos / espacios
for _i in range(1, 21):
    campo_omitido = ["nombres", "apellido_paterno", "dni", "correo"][_i % 4]
    datos = {
        "nombres": "Juan",
        "apellido_paterno": "Perez",
        "dni": f"{20000000 + _i:08d}",
        "correo": f"juan_{_i}@aurafit.pe",
    }
    datos[campo_omitido] = "   " if _i % 2 == 0 else ""
    INVALID_CASES.append((f"campo_vacio_{campo_omitido}_{_i:02d}", datos, 400))

# 2.3: 15 casos con valores nulos (None) en JSON (no debe lanzar HTTP 500 AttributeError)
for _i in range(1, 16):
    campo_nulo = ["nombres", "apellido_paterno", "dni", "correo", "sexo"][_i % 5]
    datos = {
        "nombres": "Ana",
        "apellido_paterno": "Soto",
        "dni": f"{30000000 + _i:08d}",
        "correo": f"ana_{_i}@aurafit.pe",
        "sexo": "F",
    }
    datos[campo_nulo] = None
    expected_status = 201 if campo_nulo == "sexo" else 400
    INVALID_CASES.append((f"json_valor_none_{campo_nulo}_{_i:02d}", datos, expected_status))

# 2.4: 15 casos de fecha_nacimiento con formato inválido (debe retornar 400, no 500)
for _i in range(1, 16):
    INVALID_CASES.append((
        f"fecha_nacimiento_invalida_{_i:02d}",
        {
            "nombres": "Pedro",
            "apellido_paterno": "Lara",
            "dni": f"{40000000 + _i:08d}",
            "correo": f"pedro_{_i}@aurafit.pe",
            "fecha_nacimiento": f"fecha-invalida-{_i}",
        },
        400,
    ))

# 2.5: 10 casos de form-data con incluir_membresia="false" (no debe crear membresía)
def _make_invalid_case_test(name, payload, expected_status):
    def _test(self):
        response = self.client.post(
            self.url_inscribir,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            expected_status,
            f"Fallo en caso '{name}': se esperaba HTTP {expected_status} pero devolvió HTTP {response.status_code} ({response.content.decode('utf-8', errors='ignore')})",
        )

    return _test


for _idx, (_name, _payload, _status) in enumerate(INVALID_CASES, start=1):
    setattr(
        ClientesMasivoAPITestCase,
        f"test_02_entrada_borde_{_idx:03d}_{_name}",
        _make_invalid_case_test(_name, _payload, _status),
    )


def _make_formdata_bool_test(idx):
    def _test(self):
        dni = f"{50000000 + idx:08d}"
        response = self.client.post(
            self.url_inscribir,
            data={
                "nombres": f"FormUser{idx}",
                "apellido_paterno": "FormTest",
                "dni": dni,
                "correo": f"form_{idx}@aurafit.pe",
                "incluir_membresia": "false",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIsNone(
            data["cliente"]["membresia_id"],
            "Fallo: enviar incluir_membresia='false' en form-data creó una membresía por evaluar bool('false') == True",
        )

    return _test


for _i in range(1, 11):
    setattr(
        ClientesMasivoAPITestCase,
        f"test_02_entrada_borde_{90 + _i:03d}_formdata_false_{_i:02d}",
        _make_formdata_bool_test(_i),
    )


# ============================================================================
# 3. GENERACIÓN DE 50 PRUEBAS DE CONFLICTO DE UNICIDAD (DNI Y CORREO - HTTP 409)
# ============================================================================
def _make_duplicate_test(idx):
    def _test(self):
        dni = f"{60000000 + idx:08d}"
        correo = f"duplicado_{idx}@aurafit.pe"
        Cliente.objects.create(
            nombres="Original",
            apellido_paterno="User",
            dni=dni,
            telefono="999888777",
            correo=correo,
            fecha_nacimiento=date(1995, 1, 1),
            sexo=Sexo.MASCULINO,
            direccion="Av. Original",
            estado=Estado.ACTIVO,
        )
        # Intentar duplicar DNI o correo
        payload = {
            "nombres": "Intento",
            "apellido_paterno": "Duplicado",
            "dni": dni if idx % 2 == 0 else f"{65000000 + idx:08d}",
            "correo": f"otro_{idx}@aurafit.pe" if idx % 2 == 0 else correo,
        }
        response = self.client.post(
            self.url_inscribir,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)

    return _test


for _i in range(1, 51):
    setattr(
        ClientesMasivoAPITestCase,
        f"test_03_unicidad_409_{_i:03d}",
        _make_duplicate_test(_i),
    )


# ============================================================================
# 4. GENERACIÓN DE 50 PRUEBAS DE ESTADÍSTICAS, ORDENACIÓN Y PARÁMETROS GET
# ============================================================================
def _make_orden_query_test(idx):
    def _test(self):
        for k in range(3):
            Cliente.objects.create(
                nombres=f"Orden{k}",
                apellido_paterno="Test",
                dni=f"{70000000 + idx * 10 + k:08d}",
                telefono="900000000",
                correo=f"orden_{idx}_{k}@aurafit.pe",
                fecha_nacimiento=date(1995, 5, 5),
                sexo=Sexo.MASCULINO,
                direccion="Av. Test",
                estado=Estado.ACTIVO,
            )

        if idx <= 20:
            orden = "asc" if idx % 2 == 0 else "desc"
            res = self.client.get(f"{self.url_orden}?limite={idx}&orden={orden}")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["total_inscritos"], 3)
        elif idx <= 35:
            # Límite no numérico o negativo no debe romper el servidor con HTTP 500
            bad_limit = "abc" if idx % 2 == 0 else "-5"
            res = self.client.get(f"{self.url_orden}?limite={bad_limit}")
            self.assertIn(
                res.status_code,
                (200, 400),
                f"Fallo: ?limite={bad_limit} causó HTTP {res.status_code} (Error 500 no controlado)",
            )
        else:
            res_stats = self.client.get(self.url_estadisticas)
            self.assertEqual(res_stats.status_code, 200)
            self.assertEqual(res_stats.json()["total_clientes_en_bd"], 3)

    return _test


for _i in range(1, 51):
    setattr(
        ClientesMasivoAPITestCase,
        f"test_04_estadisticas_y_orden_{_i:03d}",
        _make_orden_query_test(_i),
    )
