# 1. PROGRAMACIÓN LÓGICA (Reglas de Negocio con match-case)

def es_pago_efectivo(pago):
    """
    Evalúa el estado del pago utilizando coincidencia de patrones.
    Filtra transacciones pendientes o anuladas.
    """
    match pago.estado:
        case "PAGADO":
            return True
        case "PENDIENTE" | "ANULADO":
            return False
        case _:
            return False

def categorizar_ingreso(pago):
    """
    Evalúa y clasifica el nivel del ingreso combinando match-case con 
    guardas condicionales (if) para rangos numéricos.
    """
    monto_float = float(pago.monto)
    
    match pago.estado:
        case "PAGADO" if monto_float >= 500.0:
            return "INGRESO_ALTO_VALOR"
        case "PAGADO" if monto_float >= 100.0:
            return "INGRESO_ESTANDAR"
        case "PAGADO":
            return "INGRESO_MENOR"
        case "PENDIENTE":
            return "CUENTA_POR_COBRAR"
        case _:
            return "NO_CONTABILIZADO"

#R

def contar_pagos_completados_recursivo(lista_pagos, indice=0):
    """
    Calcula la cantidad total de pagos exitosos llamándose a sí misma.
    """
    # Caso Base: Fin de la iteración
    if indice == len(lista_pagos):
        return 0
    
    # Caso Recursivo
    es_valido = 1 if es_pago_efectivo(lista_pagos[indice]) else 0
    
    return es_valido + contar_pagos_completados_recursivo(lista_pagos, indice + 1)