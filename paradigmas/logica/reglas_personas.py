# 1. PROGRAMACIÓN LÓGICA (Reglas de Negocio con match-case)

def es_cliente_apto(cliente):
    """
    Evalúa el estado del cliente utilizando coincidencia de patrones (match).
    Retorna un booleano puro que servirá de filtro para el motor funcional.
    """
    match cliente.estado:
        case "ACTIVO":
            return True
        case "INACTIVO":
            return False
        case _:
            return False


def categorizar_entrenador(entrenador):
    """
    Evalúa y clasifica al entrenador basándose en su estado y especialidad real.
    Aplica guardas lógicas (if) dentro del match para una clasificación avanzada.
    """
    # Convertimos la especialidad a minúsculas para una evaluación segura
    especialidad_min = entrenador.especialidad.lower()

    match entrenador.estado:
        case "ACTIVO" if "musculacion" in especialidad_min or "pesas" in especialidad_min:
            return "ESPECIALISTA_FUERZA"
        case "ACTIVO" if "cardio" in especialidad_min or "crossfit" in especialidad_min:
            return "ESPECIALISTA_ALTO_RENDIMIENTO"
        case "ACTIVO":
            return "ENTRENADOR_GENERAL"
        case "INACTIVO":
            return "NO_DISPONIBLE"
        case _:
            return "ESTADO_DESCONOCIDO"


# 2. R

def contar_clientes_activos_recursivo(lista_clientes, indice=0):
    """
    Calcula la cantidad total de clientes activos 
    """
    # Caso Base: Fin de la lista (condición de parada de la recursión)
    if indice == len(lista_clientes):
        return 0
    
    # Caso Recursivo: Evaluamos mediante la regla lógica y avanzamos el índice
    es_activo = 1 if es_cliente_apto(lista_clientes[indice]) else 0
    
    return es_activo + contar_clientes_activos_recursivo(lista_clientes, indice + 1)