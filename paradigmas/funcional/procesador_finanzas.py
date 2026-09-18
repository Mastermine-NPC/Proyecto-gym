from abc import ABC, abstractmethod
from functools import reduce

# Importamos las reglas lógicas puras
from paradigmas.logica.reglas_finanzas import es_pago_efectivo, categorizar_ingreso

# 1. PARADIGMA ORIENTADO A OBJETOS (Abstracción)

class ProcesadorFinanzasBase(ABC):
    """Contrato estricto para el procesamiento del balance contable."""
    @abstractmethod
    def procesar_balance(self):
        pass

# 2. PROGRAMACIÓN FUNCIONAL Y MULTIPARADIGMA

class ProcesadorFinanzas(ProcesadorFinanzasBase):
    """
    Clase concreta que aplica transformaciones inmutables a los registros 
    financieros del gimnasio.
    """
    def __init__(self, lista_membresias, lista_pagos):
        self.membresias = lista_membresias
        self.pagos = lista_pagos

    def procesar_balance(self):
        # A) FILTER + LAMBDA (Selección Inmutable)
        membresias_activas = list(filter(lambda m: m.estado == "ACTIVA", self.membresias))
        pagos_exitosos = list(filter(lambda p: es_pago_efectivo(p), self.pagos))

        # B) MAP + LÓGICA (Transformación)
        # Extraemos un historial 
        historial_financiero = list(map(
            lambda p: {
                "ticket_id": p.id,
                "cliente": p.membresia.cliente.nombres,
                "monto_pagado": float(p.monto),
                "categoria_ingreso": categorizar_ingreso(p)
            },
            pagos_exitosos
        ))

        # C) REDUCE + LAMBDA (Agregación Funcional Avanzada)
        # Sumamos todos los montos sin usar bucles ni variables mutables.
        # El 0.0 al final es el valor inicial del acumulador (acc).
        ingreso_total = reduce(
            lambda acc, p: acc + float(p.monto), 
            pagos_exitosos, 
            0.0
        )

        # D) REDUCE + LAMBDA (Búsqueda del Máximo)
        # Encontramos el pago más alto comparando uno a uno inmutablemente.
        pago_maximo = reduce(
            lambda acc, p: float(p.monto) if float(p.monto) > acc else acc, 
            pagos_exitosos, 
            0.0
        )

        return {
            "total_membresias_vigentes": len(membresias_activas),
            "transacciones_exitosas": len(pagos_exitosos),
            "ingreso_neto_total": ingreso_total,
            "ticket_maximo_registrado": pago_maximo,
            "historial_financiero": historial_financiero
        }