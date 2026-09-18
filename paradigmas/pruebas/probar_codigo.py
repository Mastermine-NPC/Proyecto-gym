import os
import django
import json

# CONFIGURACIÓN DEL ENTORNO DJANGO

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# IMPORTACIÓN DE MODELOS

from apps.clientes.models import Cliente
from apps.entrenadores.models import Entrenador
from apps.asistencias.models import Asistencia
from apps.evaluaciones.models import EvaluacionFisica
from apps.membresias.models import Membresia
from apps.pagos.models import Pago

# IMPORTACIÓN DE LOS PARADIGMAS

from paradigmas.orquestador import OrquestadorAuraFit

from paradigmas.funcional.procesador_personas import ProcesadorPersonas
from paradigmas.funcional.procesador_operaciones import ProcesadorOperaciones
from paradigmas.funcional.procesador_finanzas import ProcesadorFinanzas

from paradigmas.logica.reglas_personas import (
    contar_clientes_activos_recursivo
)

from paradigmas.logica.reglas_operaciones import (
    contar_asistencias_efectivas_recursivo
)

from paradigmas.logica.reglas_finanzas import (
    contar_pagos_completados_recursivo
)

# PANEL DE CONTROL

def menu_interactivo():

    print("\nCargando información desde la base de datos...\n")

    clientes_bd = list(Cliente.objects.all())
    entrenadores_bd = list(Entrenador.objects.all())
    asistencias_bd = list(Asistencia.objects.all())
    evaluaciones_bd = list(EvaluacionFisica.objects.all())
    membresias_bd = list(Membresia.objects.all())
    pagos_bd = list(Pago.objects.all())

    while True:

        print("\n" + "=" * 80)
        print("        AURAFIT - PANEL DE PARADIGMAS DE PROGRAMACIÓN")
        print("=" * 80)

        print("[1] Personas      (Clientes - Entrenadores)")
        print("    Funcional | Lógica | POO")

        print("[2] Operaciones   (Asistencias - Evaluaciones)")
        print("    Funcional | Lógica")

        print("[3] Financiero    (Membresías - Pagos)")
        print("    Funcional | Lógica")

        print("[4] Orquestador")

        print("[5] Salir")

        print("=" * 80)

        opcion = input("Seleccione una opción: ")

        # PERSONAS

        if opcion == "1":

            print("\n" + "=" * 100)
            print("MÓDULO PERSONAS")
            print("=" * 100)
            print("Entidades procesadas : Clientes y Entrenadores")
            print("Paradigmas utilizados:")
            print(" • Programación Funcional")
            print(" • Programación Lógica")
            print(" • Programación Orientada a Objetos")
            print("=" * 100 + "\n")

            motor = ProcesadorPersonas(
                clientes_bd,
                entrenadores_bd
            )

            resultado = motor.procesar()

            print(json.dumps(resultado, indent=4, ensure_ascii=False))

            print("\nResultado de la función recursiva")
            print(
                f"Clientes activos encontrados: "
                f"{contar_clientes_activos_recursivo(clientes_bd)}"
            )

            input("\nPresione ENTER para continuar...")

        # OPERACIONES

        elif opcion == "2":

            print("\n" + "=" * 100)
            print("MÓDULO OPERACIONES")
            print("=" * 100)
            print("Entidades procesadas : Asistencias y Evaluaciones")
            print("Paradigmas utilizados:")
            print(" • Programación Funcional")
            print(" • Programación Lógica")
            print("=" * 100 + "\n")

            motor = ProcesadorOperaciones(
                asistencias_bd,
                evaluaciones_bd
            )

            resultado = motor.procesar()

            print(json.dumps(resultado, indent=4, ensure_ascii=False))

            print("\nResultado de la función recursiva")
            print(
                f"Asistencias efectivas encontradas: "
                f"{contar_asistencias_efectivas_recursivo(asistencias_bd)}"
            )

            input("\nPresione ENTER para continuar...")

        # FINANZAS

        elif opcion == "3":

            print("\n" + "=" * 100)
            print("MÓDULO FINANCIERO")
            print("=" * 100)
            print("Entidades procesadas : Membresías y Pagos")
            print("Paradigmas utilizados:")
            print(" • Programación Funcional")
            print(" • Programación Lógica")
            print("=" * 100 + "\n")

            motor = ProcesadorFinanzas(
                membresias_bd,
                pagos_bd
            )

            resultado = motor.procesar_balance()

            print(json.dumps(resultado, indent=4, ensure_ascii=False))

            print("\nResultado de la función recursiva")
            print(
                f"Pagos completados encontrados: "
                f"{contar_pagos_completados_recursivo(pagos_bd)}"
            )

            input("\nPresione ENTER para continuar...")

        # ORQUESTADOR

        elif opcion == "4":

            print("\n" + "=" * 100)
            print("ORQUESTADOR DEL SISTEMA")
            print("=" * 100)
            print("Este módulo integra la información procesada por:")
            print(" • Personas")
            print(" • Operaciones")
            print(" • Finanzas")
            print("=" * 100 + "\n")

            sistema = OrquestadorAuraFit(
                clientes_bd,
                entrenadores_bd,
                asistencias_bd,
                evaluaciones_bd,
                membresias_bd,
                pagos_bd
            )

            reporte = sistema.generar_reporte_integral()

            print(json.dumps(reporte, indent=4, ensure_ascii=False))

            input("\nPresione ENTER para continuar...")

        # SALIR

        elif opcion == "5":

            print("\nGracias por utilizar AuraFit.")
            print("Cierre del sistema realizado correctamente.\n")
            break

        # OPCIÓN INVÁLIDA

        else:

            print("\n[ERROR] La opción ingresada no es válida.")
            print("Por favor, seleccione una opción del 1 al 5.\n")

# EJECUCIÓN DEL PROGRAMA

if __name__ == "__main__":
    menu_interactivo()