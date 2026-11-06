import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from apps.clientes.models import Cliente, Sexo, Estado
from apps.membresias.models import Membresia, TipoMembresia


class ClientesAPITestCase(TestCase):
    """
    Pruebas de integración y modelos para el módulo de Clientes y Membresías.
    """

    def setUp(self):
        self.client = Client()
        self.url_inscribir = reverse("clientes:inscribir_cliente")
        self.url_estadisticas = reverse("clientes:estadisticas_clientes")
        self.url_orden = reverse("clientes:api_orden_inscripciones")
        self.url_auditoria = reverse("auditoria")

    def test_inscribir_cliente_exitoso_con_membresia(self):
        payload = {
            "nombres": "Carlos",
            "apellido_paterno": "Mendoza",
            "apellido_materno": "Rojas",
            "dni": "12345678",
            "telefono": "987654321",
            "correo": "carlos.mendoza@aurafit.pe",
            "fecha_nacimiento": "1995-05-15",
            "sexo": "M",
            "direccion": "Av. Arequipa 1200",
            "incluir_membresia": True,
        }
        response = self.client.post(
            self.url_inscribir,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["cliente"]["dni"], "12345678")
        self.assertIsNotNone(data["cliente"]["membresia_id"])
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Membresia.objects.count(), 1)

    def test_inscribir_cliente_dni_invalido(self):
        payload = {
            "nombres": "Ana",
            "apellido_paterno": "Torres",
            "dni": "1234",  # Menos de 8 dígitos
            "correo": "ana.torres@aurafit.pe",
        }
        response = self.client.post(
            self.url_inscribir,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_inscribir_cliente_duplicado_retorna_409(self):
        Cliente.objects.create(
            nombres="Luis",
            apellido_paterno="Gomez",
            apellido_materno="Diaz",
            dni="87654321",
            telefono="999111222",
            correo="luis@aurafit.pe",
            fecha_nacimiento=date(1992, 3, 10),
            sexo=Sexo.MASCULINO,
            direccion="Jr. Union 456",
            estado=Estado.ACTIVO,
        )
        payload = {
            "nombres": "Luis",
            "apellido_paterno": "Gomez",
            "dni": "87654321",
            "correo": "luis@aurafit.pe",
        }
        response = self.client.post(
            self.url_inscribir,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)

    def test_estadisticas_y_orden_inscripciones(self):
        Cliente.objects.create(
            nombres="Maria",
            apellido_paterno="Vargas",
            apellido_materno="Luna",
            dni="11223344",
            telefono="911223344",
            correo="maria@aurafit.pe",
            fecha_nacimiento=date(1999, 8, 20),
            sexo=Sexo.FEMENINO,
            direccion="Calle Los Pinos 101",
            estado=Estado.ACTIVO,
        )
        res_stats = self.client.get(self.url_estadisticas)
        self.assertEqual(res_stats.status_code, 200)
        self.assertEqual(res_stats.json()["total_clientes_en_bd"], 1)

        res_orden = self.client.get(f"{self.url_orden}?limite=10&orden=asc")
        self.assertEqual(res_orden.status_code, 200)
        orden_data = res_orden.json()
        self.assertEqual(orden_data["total_inscritos"], 1)
        self.assertEqual(orden_data["primero"]["dni"], "11223344")

    def test_vista_auditoria_concurrencia(self):
        response = self.client.get(self.url_auditoria)
        self.assertEqual(response.status_code, 200)
        self.assertIn("AuraFit Gym", response.content.decode("utf-8"))
