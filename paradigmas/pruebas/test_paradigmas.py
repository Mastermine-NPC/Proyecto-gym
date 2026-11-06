from datetime import date, time, timedelta
from decimal import Decimal
from django.test import TestCase

from apps.clientes.models import Cliente, Sexo, Estado as EstadoCliente
from apps.entrenadores.models import Entrenador, Estado as EstadoEntrenador
from apps.asistencias.models import Asistencia, EstadoAsistencia
from apps.evaluaciones.models import EvaluacionFisica, EstadoEvaluacion
from apps.membresias.models import Membresia, TipoMembresia, EstadoMembresia
from apps.pagos.models import Pago, MetodoPago, EstadoPago

from paradigmas.orquestador import OrquestadorAuraFit
from paradigmas.logica.reglas_personas import contar_clientes_activos_recursivo
from paradigmas.logica.reglas_operaciones import contar_asistencias_efectivas_recursivo
from paradigmas.logica.reglas_finanzas import contar_pagos_completados_recursivo


class ParadigmasAuraFitTestCase(TestCase):
    """
    Pruebas automatizadas para los módulos de Programación Funcional,
    Programación Lógica (match-case y recursividad) y POO (OrquestadorAuraFit).
    """

    def setUp(self):
        self.cliente_activo = Cliente.objects.create(
            nombres="Diego",
            apellido_paterno="Salazar",
            apellido_materno="Quispe",
            dni="44556677",
            telefono="944556677",
            correo="diego@aurafit.pe",
            fecha_nacimiento=date(1996, 4, 12),
            sexo=Sexo.MASCULINO,
            direccion="Av. Javier Prado 500",
            estado=EstadoCliente.ACTIVO,
        )
        self.cliente_inactivo = Cliente.objects.create(
            nombres="Pedro",
            apellido_paterno="Castillo",
            apellido_materno="Perez",
            dni="99887766",
            telefono="999887766",
            correo="pedro@aurafit.pe",
            fecha_nacimiento=date(1990, 1, 20),
            sexo=Sexo.MASCULINO,
            direccion="Av. Brasil 300",
            estado=EstadoCliente.INACTIVO,
        )

        self.entrenador_fuerza = Entrenador.objects.create(
            nombres="Roberto",
            apellido_paterno="Campos",
            apellido_materno="Vega",
            telefono="912345678",
            especialidad="Musculacion y Pesas",
            fecha_contratacion=date(2023, 1, 15),
            estado=EstadoEntrenador.ACTIVO,
        )

        self.asistencia_ok = Asistencia.objects.create(
            cliente=self.cliente_activo,
            fecha=date.today(),
            hora_ingreso=time(8, 30),
            estado=EstadoAsistencia.REGISTRADA,
        )

        self.evaluacion = EvaluacionFisica.objects.create(
            cliente=self.cliente_activo,
            entrenador=self.entrenador_fuerza,
            fecha=date.today(),
            peso=Decimal("74.50"),
            estatura=Decimal("1.75"),
            porcentaje_grasa=Decimal("14.20"),
            masa_muscular=Decimal("38.00"),
            estado=EstadoEvaluacion.ACTIVA,
        )

        self.tipo_membresia = TipoMembresia.objects.create(
            nombre="Plan Trimestral Pro",
            precio=Decimal("300.00"),
            duracion_dias=90,
        )
        self.membresia = Membresia.objects.create(
            cliente=self.cliente_activo,
            tipo_membresia=self.tipo_membresia,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            estado=EstadoMembresia.ACTIVA,
        )

        self.metodo_pago = MetodoPago.objects.create(nombre="Tarjeta / Yape")
        self.pago = Pago.objects.create(
            membresia=self.membresia,
            metodo_pago=self.metodo_pago,
            monto=Decimal("300.00"),
            fecha_pago=date.today(),
            estado=EstadoPago.PAGADO,
        )

    def test_funciones_recursivas_y_reglas_logicas(self):
        clientes = list(Cliente.objects.all())
        asistencias = list(Asistencia.objects.all())
        pagos = list(Pago.objects.all())

        self.assertEqual(contar_clientes_activos_recursivo(clientes), 1)
        self.assertEqual(contar_asistencias_efectivas_recursivo(asistencias), 1)
        self.assertEqual(contar_pagos_completados_recursivo(pagos), 1)

    def test_orquestador_reporte_integral(self):
        orquestador = OrquestadorAuraFit(
            list(Cliente.objects.all()),
            list(Entrenador.objects.all()),
            list(Asistencia.objects.all()),
            list(EvaluacionFisica.objects.all()),
            list(Membresia.objects.all()),
            list(Pago.objects.all()),
        )
        reporte = orquestador.generar_reporte_integral()
        self.assertIn("GIMNASIO_AURAFIT", reporte)

        datos = reporte["GIMNASIO_AURAFIT"]
        self.assertEqual(datos["MODULO_PERSONAS"]["total_clientes_filtrados"], 1)
        self.assertEqual(
            datos["MODULO_PERSONAS"]["plantilla_tecnica"][0]["rango_asignado"],
            "ESPECIALISTA_FUERZA",
        )
        self.assertEqual(datos["MODULO_OPERACIONES"]["total_asistencias_validas"], 1)
        self.assertEqual(
            datos["MODULO_OPERACIONES"]["reporte_salud"][0]["diagnostico"],
            "NIVEL_ATLETICO",
        )
        self.assertEqual(datos["MODULO_FINANCIERO"]["ingreso_neto_total"], 300.0)
        self.assertEqual(
            datos["MODULO_FINANCIERO"]["historial_financiero"][0]["categoria_ingreso"],
            "INGRESO_ESTANDAR",
        )
