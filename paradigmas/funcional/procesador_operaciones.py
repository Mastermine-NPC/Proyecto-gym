"""
Proyecto: AuraFit
Curso: Lenguajes de Programación
Autores: Fernando Jose Concha Jimenez / Sebastian Chambi Mamani

Descripción:
Módulo Funcional Multiparadigma para la transformación de 'Asistencias' y 'Evaluaciones'.
Integra POO (Clases Abstractas), Funciones de Orden Superior (map, filter) y
el iterador 'zip' para emparejar datos de forma inmutable y paralela.
"""
from abc import ABC, abstractmethod

# Importamos las reglas lógicas puras
from paradigmas.logica.reglas_operaciones import es_asistencia_efectiva, evaluar_imc_y_grasa

# 1. PARADIGMA ORIENTADO A OBJETOS

class ProcesadorOperacionesBase(ABC):
    """Interfaz abstracta que obliga a implementar la generación del historial."""
    @abstractmethod
    def procesar(self):
        pass

# 2. PROGRAMACIÓN FUNCIONAL Y MULTIPARADIGMA

class ProcesadorOperaciones(ProcesadorOperacionesBase):
    """
    Clase concreta que aplica transformaciones inmutables a los registros 
    operativos del gimnasio.
    """
    def __init__(self, lista_asistencias, lista_evaluaciones):
        self.asistencias = lista_asistencias
        self.evaluaciones = lista_evaluaciones

    def procesar(self):
        # A) FILTER + LAMBDA 
        asistencias_validas = list(filter(lambda a: es_asistencia_efectiva(a), self.asistencias))
        evaluaciones_activas = list(filter(lambda e: e.estado == "ACTIVA", self.evaluaciones))

        # B) MAP + LAMBDA (Transformación de Asistencias)
        reporte_asistencias = list(map(
            lambda a: f"Cliente: {a.cliente.nombres} | Fecha: {a.fecha.strftime('%d/%m/%Y')} | Ingreso: {a.hora_ingreso}",
            asistencias_validas
        ))

        # C) MAP + LÓGICA (Extracción de diagnósticos)
        # Obtenemos una lista paralela puramente con las clasificaciones lógicas
        diagnosticos = list(map(
            lambda e: evaluar_imc_y_grasa(e),
            evaluaciones_activas
        ))

        # D) ZIP Iteración paralela 
        # Emparejamos cada evaluación (objeto) con su diagnóstico (cadena)
        # sin modificar el objeto original, creando tuplas (Evaluacion, Diagnostico)
        reporte_tuplas_zip = list(zip(evaluaciones_activas, diagnosticos))

        # E) MAP SOBRE ZIP (Empaquetado final)
        reporte_medico_final = list(map(
            lambda item: {
                "cliente": item[0].cliente.nombres,
                "fecha": item[0].fecha.strftime("%d/%m/%Y"),
                "peso_kg": float(item[0].peso),
                "estatura_m": float(item[0].estatura),
                "diagnostico": item[1] # El diagnóstico extraído del zip
            },
            reporte_tuplas_zip
        ))

        return {
            "total_asistencias_validas": len(reporte_asistencias),
            "registro_ingresos": reporte_asistencias,
            "total_evaluaciones_procesadas": len(reporte_medico_final),
            "reporte_salud": reporte_medico_final
        }