"""
Proyecto: AuraFit
Curso: Lenguajes de Programación
Autores: Fernando Jose Concha Jimenez / Sebastian Chambi Mamani

Descripción:
Orquestador Principal del Sistema (Patrón Facade).
Unifica los tres dominios de negocio: Personas, Operaciones y Finanzas.
"""

from paradigmas.funcional.procesador_personas import ProcesadorPersonas
from paradigmas.funcional.procesador_operaciones import ProcesadorOperaciones
from paradigmas.funcional.procesador_finanzas import ProcesadorFinanzas


class OrquestadorAuraFit:
    """
    Clase central que coordina la ejecución de todos los paradigmas del sistema.
    """
    def __init__(self, clientes, entrenadores, asistencias, evaluaciones, membresias, pagos):
        self.clientes = clientes
        self.entrenadores = entrenadores
        self.asistencias = asistencias
        self.evaluaciones = evaluaciones
        self.membresias = membresias
        self.pagos = pagos

    def generar_reporte_integral(self):
        """
        Ejecuta el pipeline completo de procesamiento funcional y lógico.
        """
        # 1. Instanciamos los procesadores
        motor_personas = ProcesadorPersonas(self.clientes, self.entrenadores)
        motor_operaciones = ProcesadorOperaciones(self.asistencias, self.evaluaciones)
        motor_finanzas = ProcesadorFinanzas(self.membresias, self.pagos)

        # 2. Ejecutamos las transformaciones
        reporte_personas = motor_personas.procesar()
        reporte_operaciones = motor_operaciones.procesar()
        reporte_finanzas = motor_finanzas.procesar_balance()

        # 3. Empaquetamos en el reporte maestro
        return {
            "GIMNASIO_AURAFIT": {
                "MODULO_PERSONAS": reporte_personas,
                "MODULO_OPERACIONES": reporte_operaciones,
                "MODULO_FINANCIERO": reporte_finanzas
            }
        }