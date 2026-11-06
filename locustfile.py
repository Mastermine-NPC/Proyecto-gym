"""
================================================================================
AURAFIT GYM - PRUEBA DE CONCURRENCIA CON LOCUST
Simulación de 1,000 usuarios concurrentes inscribiéndose simultáneamente
y registrando transacciones en la Base de Datos.
================================================================================
"""

import itertools
import random
import time
from locust import HttpUser, task, between, events

# Generador atómico / secuencial para DNI único (evita colisiones por UNIQUE en BD)
# Comienza en un rango aleatorio para no colisionar con ejecuciones previas
_DNI_BASE = random.randint(20000000, 70000000)
_contador_dni = itertools.count(_DNI_BASE)

NOMBRES_POOL = [
    "Carlos", "Ana", "Mateo", "Valeria", "Diego", "Lucia", "Jorge", "Camila",
    "Luis", "Sofia", "Alejandro", "Maria", "Gabriel", "Elena", "Fernando",
    "Andrea", "Rodrigo", "Paula", "Sebastian", "Daniela", "Alonso", "Natalia"
]

APELLIDOS_POOL = [
    "García", "Flores", "Rodríguez", "Quispe", "Mendoza", "Morales", "Castillo",
    "Sánchez", "Vargas", "Reyes", "Gutiérrez", "Chávez", "Ramos", "Espinoza",
    "Torres", "Díaz", "Aguilar", "Medina", "Vega", "Castro", "Romero", "Paredes"
]

DISTRITOS_POOL = [
    "Av. Javier Prado 1420, San Isidro",
    "Av. Benavides 2340, Miraflores",
    "Av. La Marina 1890, San Miguel",
    "Jr. Huancavelica 512, Lima Centro",
    "Av. Universitaria 3100, Los Olivos",
    "Calle Las Begonias 450, San Isidro",
    "Av. Arequipa 3800, Lince",
    "Av. Primavera 980, Surco"
]


class ClienteGimnasioUser(HttpUser):
    """
    Representa a un usuario virtual que se conecta al sistema del gimnasio
    y realiza el proceso de inscripción en la Base de Datos.
    """

    # Tiempo de espera entre tareas (simula el comportamiento real de usuarios)
    wait_time = between(0.1, 1.0)

    @task(10)
    def inscribir_cliente(self):
        """
        Envía una solicitud POST concurrente para inscribir un nuevo cliente.
        Se generan datos únicos y válidos para cada cliente.
        """
        dni_num = next(_contador_dni)
        dni_str = f"{dni_num % 100000000:08d}"
        nombre = random.choice(NOMBRES_POOL)
        ape_paterno = random.choice(APELLIDOS_POOL)
        ape_materno = random.choice(APELLIDOS_POOL)
        sexo = random.choice(["M", "F"])
        email = f"cliente_{dni_str}_{random.randint(100, 999)}@testgym.com"
        telefono = f"9{random.randint(10000000, 99999999)}"

        payload = {
            "nombres": nombre,
            "apellido_paterno": ape_paterno,
            "apellido_materno": ape_materno,
            "dni": dni_str,
            "telefono": telefono,
            "correo": email,
            "fecha_nacimiento": f"{random.randint(1980, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "sexo": sexo,
            "direccion": random.choice(DISTRITOS_POOL),
            "incluir_membresia": True  # Inscribe también membresía en BD
        }

        # Medición del tiempo y ejecución HTTP POST
        with self.client.post(
            "/api/clientes/inscribir/",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /api/clientes/inscribir/ (Inscripción en BD)"
        ) as response:
            if response.status_code == 201:
                try:
                    data = response.json()
                    if data.get("status") == "success":
                        response.success()
                    else:
                        response.failure(f"Respuesta inesperada: {response.text}")
                except Exception as ex:
                    response.failure(f"Error al decodificar JSON: {ex}")
            elif response.status_code == 409:
                # Conflicto de unicidad
                response.failure("Conflicto de unicidad en base de datos (DNI o Correo duplicado)")
            else:
                response.failure(f"Fallo en la inscripción HTTP {response.status_code}: {response.text}")

    @task(1)
    def consultar_estadisticas_bd(self):
        """
        Consulta periódica para monitorear el total de clientes registrados
        en tiempo real directamente desde la base de datos.
        """
        with self.client.get(
            "/api/clientes/estadisticas/",
            catch_response=True,
            name="GET /api/clientes/estadisticas/ (Conteo en BD)"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Fallo al consultar estadísticas HTTP {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "=" * 80)
    print(" INICIANDO PRUEBA DE CONCURRENCIA LOCUST - GIMNASIO AURAFIT")
    print(" Objetivo: 1,000 usuarios concurrentes inscribiéndose en la BD")
    print(f" Host objetivo: {environment.host}")
    print("=" * 80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "=" * 80)
    print(" PRUEBA DE CONCURRENCIA FINALIZADA")
    print(" Revise el resumen de latencia, requests/segundo y tasa de éxito.")
    print("=" * 80 + "\n")
