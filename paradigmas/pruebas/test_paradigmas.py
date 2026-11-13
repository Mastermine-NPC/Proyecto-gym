from datetime import date, time, timedelta
from decimal import Decimal
from types import SimpleNamespace
from django.test import TestCase

from apps.clientes.models import Cliente, Sexo, Estado as EstadoCliente
from apps.entrenadores.models import Entrenador, Estado as EstadoEntrenador
from apps.asistencias.models import Asistencia, EstadoAsistencia
from apps.evaluaciones.models import EvaluacionFisica, EstadoEvaluacion
from apps.membresias.models import Membresia, TipoMembresia, EstadoMembresia
from apps.pagos.models import Pago, MetodoPago, EstadoPago

from paradigmas.orquestador import OrquestadorAuraFit
from paradigmas.funcional.procesador_personas import ProcesadorPersonas
from paradigmas.funcional.procesador_operaciones import ProcesadorOperaciones
from paradigmas.funcional.procesador_finanzas import ProcesadorFinanzas
from paradigmas.logica.reglas_personas import (
    es_cliente_apto,
    categorizar_entrenador,
    contar_clientes_activos_recursivo,
)
from paradigmas.logica.reglas_operaciones import (
    es_asistencia_efectiva,
    evaluar_imc_y_grasa,
    contar_asistencias_efectivas_recursivo,
)
from paradigmas.logica.reglas_finanzas import (
    es_pago_efectivo,
    categorizar_ingreso,
    contar_pagos_completados_recursivo,
)


class ParadigmasMasivoTestCase(TestCase):
    """
    Suite exhaustiva de 550 pruebas automatizadas para evaluar Reglas Lógicas,
    Procesadores Funcionales, Orquestador POO y Recursividad a escala (hasta 1,200 registros).
    """
    pass


# ============================================================================
# 1. 200 PRUEBAS DE REGLAS LÓGICAS (MATCH-CASE Y GUARDAS)
# ============================================================================
def _make_regla_persona_test(idx):
    def _test(self):
        estado = "ACTIVO" if idx % 2 == 0 else ("INACTIVO" if idx % 3 == 0 else "OTRO")
        cliente_mock = SimpleNamespace(estado=estado)
        self.assertEqual(es_cliente_apto(cliente_mock), estado == "ACTIVO")

        especialidades = [
            ("Musculacion Avanzada", "ESPECIALISTA_FUERZA"),
            ("Entrenamiento de Pesas", "ESPECIALISTA_FUERZA"),
            ("Cardio HIIT", "ESPECIALISTA_ALTO_RENDIMIENTO"),
            ("Crossfit Pro", "ESPECIALISTA_ALTO_RENDIMIENTO"),
            ("Yoga y Pilates", "ENTRENADOR_GENERAL"),
        ]
        esp_nombre, esp_esperada = especialidades[idx % len(especialidades)]
        entrenador_mock = SimpleNamespace(estado=estado, especialidad=esp_nombre)
        if estado == "ACTIVO":
            self.assertEqual(categorizar_entrenador(entrenador_mock), esp_esperada)
        elif estado == "INACTIVO":
            self.assertEqual(categorizar_entrenador(entrenador_mock), "NO_DISPONIBLE")
        else:
            self.assertEqual(categorizar_entrenador(entrenador_mock), "ESTADO_DESCONOCIDO")

    return _test


for _i in range(1, 71):
    setattr(
        ParadigmasMasivoTestCase,
        f"test_01_reglas_personas_{_i:03d}",
        _make_regla_persona_test(_i),
    )


def _make_regla_operacion_test(idx):
    def _test(self):
        est_asist = "REGISTRADA" if idx % 2 == 0 else "ANULADA"
        asist_mock = SimpleNamespace(estado=est_asist)
        self.assertEqual(es_asistencia_efectiva(asist_mock), est_asist == "REGISTRADA")

        grasa = Decimal(str(5.0 + (idx * 0.5))) if idx % 10 != 0 else None
        est_eval = "ACTIVA" if idx % 4 != 0 else "ANULADA"
        eval_mock = SimpleNamespace(estado=est_eval, porcentaje_grasa=grasa)
        res = evaluar_imc_y_grasa(eval_mock)
        if est_eval == "ANULADA":
            self.assertEqual(res, "EVALUACION_DESCARTADA")
        elif grasa is not None and grasa < 15.0:
            self.assertEqual(res, "NIVEL_ATLETICO")
        elif grasa is not None and grasa <= 25.0:
            self.assertEqual(res, "NIVEL_FITNESS")
        else:
            self.assertEqual(res, "NIVEL_ESTANDAR")

    return _test


for _i in range(1, 66):
    setattr(
        ParadigmasMasivoTestCase,
        f"test_02_reglas_operaciones_{_i:03d}",
        _make_regla_operacion_test(_i),
    )


def _make_regla_finanzas_test(idx):
    def _test(self):
        monto = Decimal(str(idx * 15.5))
        estados = ["PAGADO", "PENDIENTE", "ANULADO"]
        estado = estados[idx % 3]
        pago_mock = SimpleNamespace(estado=estado, monto=monto)
        self.assertEqual(es_pago_efectivo(pago_mock), estado == "PAGADO")

        cat = categorizar_ingreso(pago_mock)
        if estado == "PAGADO" and float(monto) >= 500.0:
            self.assertEqual(cat, "INGRESO_ALTO_VALOR")
        elif estado == "PAGADO" and float(monto) >= 100.0:
            self.assertEqual(cat, "INGRESO_ESTANDAR")
        elif estado == "PAGADO":
            self.assertEqual(cat, "INGRESO_MENOR")
        elif estado == "PENDIENTE":
            self.assertEqual(cat, "CUENTA_POR_COBRAR")
        else:
            self.assertEqual(cat, "NO_CONTABILIZADO")

    return _test


for _i in range(1, 66):
    setattr(
        ParadigmasMasivoTestCase,
        f"test_03_reglas_finanzas_{_i:03d}",
        _make_regla_finanzas_test(_i),
    )


# ============================================================================
# 2. 200 PRUEBAS DE PROCESADORES FUNCIONALES Y ORQUESTADOR MULTIPARADIGMA
# ============================================================================
def _make_orquestador_test(idx):
    def _test(self):
        n_activos = idx % 15
        n_inactivos = idx % 7
        clientes = [
            SimpleNamespace(
                nombres=f"Nom{k}",
                apellido_paterno=f"Pat{k}",
                apellido_materno=f"Mat{k}",
                telefono=f"90000{k:04d}",
                estado="ACTIVO",
            )
            for k in range(n_activos)
        ] + [
            SimpleNamespace(
                nombres=f"Inac{k}",
                apellido_paterno="Pat",
                apellido_materno="Mat",
                telefono="900000000",
                estado="INACTIVO",
            )
            for k in range(n_inactivos)
        ]

        entrenadores = [
            SimpleNamespace(
                nombres=f"Ent{k}",
                apellido_paterno=f"Ape{k}",
                especialidad="Crossfit" if k % 2 == 0 else "Pesas",
                estado="ACTIVO",
            )
            for k in range((idx % 5) + 1)
        ]

        asistencias = [
            SimpleNamespace(
                cliente=SimpleNamespace(nombres=f"Nom{k}"),
                fecha=date(2026, 1, (k % 28) + 1),
                hora_ingreso=time(8, k % 60),
                estado="REGISTRADA" if k % 2 == 0 else "ANULADA",
            )
            for k in range(idx % 20)
        ]

        evaluaciones = [
            SimpleNamespace(
                cliente=SimpleNamespace(nombres=f"Nom{k}"),
                fecha=date(2026, 2, (k % 28) + 1),
                peso=Decimal("70.0"),
                estatura=Decimal("1.75"),
                porcentaje_grasa=Decimal("12.5") if k % 2 == 0 else Decimal("22.0"),
                estado="ACTIVA",
            )
            for k in range(idx % 12)
        ]

        membresias = [
            SimpleNamespace(estado="ACTIVA" if k % 3 != 0 else "VENCIDA")
            for k in range(idx % 18)
        ]

        pagos = [
            SimpleNamespace(
                id=k + 1,
                membresia=SimpleNamespace(cliente=SimpleNamespace(nombres=f"Nom{k}")),
                monto=Decimal(str((k + 1) * 50)),
                estado="PAGADO" if k % 2 == 0 else "PENDIENTE",
            )
            for k in range(idx % 16)
        ]

        orq = OrquestadorAuraFit(
            clientes, entrenadores, asistencias, evaluaciones, membresias, pagos
        )
        rep = orq.generar_reporte_integral()["GIMNASIO_AURAFIT"]
        self.assertEqual(rep["MODULO_PERSONAS"]["total_clientes_filtrados"], n_activos)
        self.assertEqual(rep["MODULO_PERSONAS"]["total_entrenadores"], len(entrenadores))
        self.assertEqual(
            rep["MODULO_OPERACIONES"]["total_evaluaciones_procesadas"], len(evaluaciones)
        )
        pagos_ok = [p for p in pagos if p.estado == "PAGADO"]
        self.assertEqual(rep["MODULO_FINANCIERO"]["transacciones_exitosas"], len(pagos_ok))

    return _test


for _i in range(1, 201):
    setattr(
        ParadigmasMasivoTestCase,
        f"test_04_orquestador_funcional_{_i:03d}",
        _make_orquestador_test(_i),
    )


# ============================================================================
# 3. 150 PRUEBAS DE RECURSIVIDAD Y ESCALA (DESDE 10 HASTA 1,500 REGISTROS)
#    (Incluye el escenario de 1,000+ registros de concurrencia del proyecto)
# ============================================================================
def _make_recursion_scale_test(idx):
    def _test(self):
        # Escala desde 10 hasta 1,500 elementos (pasando por 1,000+)
        cantidad = idx * 10
        clientes = [
            SimpleNamespace(estado="ACTIVO" if k % 2 == 0 else "INACTIVO")
            for k in range(cantidad)
        ]
        asistencias = [
            SimpleNamespace(estado="REGISTRADA" if k % 3 != 0 else "ANULADA")
            for k in range(cantidad)
        ]
        pagos = [
            SimpleNamespace(estado="PAGADO" if k % 4 != 0 else "ANULADO")
            for k in range(cantidad)
        ]

        esperados_cli = sum(1 for c in clientes if c.estado == "ACTIVO")
        esperados_asi = sum(1 for a in asistencias if a.estado == "REGISTRADA")
        esperados_pag = sum(1 for p in pagos if p.estado == "PAGADO")

        self.assertEqual(contar_clientes_activos_recursivo(clientes), esperados_cli)
        self.assertEqual(contar_asistencias_efectivas_recursivo(asistencias), esperados_asi)
        self.assertEqual(contar_pagos_completados_recursivo(pagos), esperados_pag)

    return _test


for _i in range(1, 151):
    setattr(
        ParadigmasMasivoTestCase,
        f"test_05_recursividad_escala_{_i:03d}_{_i * 10}_registros",
        _make_recursion_scale_test(_i),
    )
