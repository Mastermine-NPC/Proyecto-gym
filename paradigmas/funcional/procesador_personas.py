"""
Proyecto: AuraFit
Curso: Lenguajes de Programación
Autores: Fernando Jose Concha Jimenez / Sebastian Chambi Mamani

Descripción:
Módulo Funcional Multiparadigma para la transformación de 'Cliente' y 'Entrenador'.
Integra POO (Clases Abstractas), Funciones de Orden Superior (map, filter, lambdas)
y el uso de iteradores (enumerate). Opera en sinergia con el módulo lógico, 
sin mutar las listas originales obtenidas de la base de datos.
"""

from abc import ABC, abstractmethod

# Importamos las reglas lógicas puras del paquete hermano
from paradigmas.logica.reglas_personas import es_cliente_apto, categorizar_entrenador

# 1. PARADIGMA ORIENTADO A OBJETOS

class ProcesadorBase(ABC):
    """
    Contrato estricto que obliga a las clases hijas a implementar
    el método 'procesar', garantizando el polimorfismo.
    """
    @abstractmethod
    def procesar(self):
        pass

# 2. PROGRAMACIÓN FUNCIONAL Y MULTIPARADIGMA 

class ProcesadorPersonas(ProcesadorBase):
    """
    Clase concreta que aplica transformaciones inmutables a los usuarios
    basándose en las reglas de negocio lógicas.
    """
    def __init__(self, lista_clientes, lista_entrenadores):
        self.clientes = lista_clientes
        self.entrenadores = lista_entrenadores

    def procesar(self):
        # A) FILTER + LAMBDA 
        # Filtramos delegando la decisión a la función pura del módulo lógico
        clientes_activos = list(filter(lambda c: es_cliente_apto(c), self.clientes))

        # B) MAP + LAMBDA (Transformación de Datos)
        # Formateamos el nombre combinando atributos reales del modelo y usando strip()/upper()
        clientes_formateados = list(map(
            lambda c: {
                "nombre_completo": f"{c.nombres} {c.apellido_paterno} {c.apellido_materno}".strip().upper(),
                "contacto_telefonico": c.telefono
            },
            clientes_activos
        ))

        # C) ENUMERATE + MAP + LÓGICA 
        # Usamos enumerate() para generar un ID interno temporal para los entrenadores
        # y mapeamos el resultado inyectando la categoría lógica de 'reglas_personas'
        plantilla_entrenadores = list(map(
            lambda item: {
                "id_interno": item[0],  # Índice generado por enumerate
                "profesional": f"{item[1].nombres} {item[1].apellido_paterno}",
                "rango_asignado": categorizar_entrenador(item[1])
            },
            enumerate(self.entrenadores, start=1)
        ))

        # Retornamos un diccionario empaquetado con las estructuras lineales procesadas
        return {
            "total_clientes_filtrados": len(clientes_formateados),
            "directorio_activos": clientes_formateados,
            "total_entrenadores": len(plantilla_entrenadores),
            "plantilla_tecnica": plantilla_entrenadores
        }