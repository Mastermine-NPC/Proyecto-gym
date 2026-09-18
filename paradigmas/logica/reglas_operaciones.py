# 1. PROGRAMACIÓN LÓGICA (Reglas de Negocio con match-case)

def es_asistencia_efectiva(asistencia):
    """
    Evalúa el estado de la asistencia utilizando coincidencia de patrones (match).
    Retorna un booleano que servirá de filtro estricto.
    """
    match asistencia.estado:
        case "REGISTRADA":
            return True
        case "ANULADA":
            return False
        case _:
            return False

def evaluar_imc_y_grasa(evaluacion):
    """
    Combina lógica de negocio evaluando atributos que pueden ser nulos (blank=True) 
    y rangos numéricos dentro de un mismo match-case.
    """
    match evaluacion.estado:
        case "ACTIVA" if evaluacion.porcentaje_grasa is not None and evaluacion.porcentaje_grasa < 15.0:
            return "NIVEL_ATLETICO"
        case "ACTIVA" if evaluacion.porcentaje_grasa is not None and evaluacion.porcentaje_grasa <= 25.0:
            return "NIVEL_FITNESS"
        case "ACTIVA":
            return "NIVEL_ESTANDAR"
        case "ANULADA":
            return "EVALUACION_DESCARTADA"
        case _:
            return "ESTADO_DESCONOCIDO"

# 2. R

def contar_asistencias_efectivas_recursivo(lista_asistencias, indice=0):
    """
    Calcula la cantidad total de asistencias válidas llamándose a sí misma.
    """
    # Caso Base
    if indice == len(lista_asistencias):
        return 0
    
    # Caso Recursivo
    es_valida = 1 if es_asistencia_efectiva(lista_asistencias[indice]) else 0
    
    return es_valida + contar_asistencias_efectivas_recursivo(lista_asistencias, indice + 1)