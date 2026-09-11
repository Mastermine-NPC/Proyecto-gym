"""
Proyecto: AuraFit
Curso: Lenguajes de Programación
Autor: Sebastian Chambi Mamani

Descripción:
Modelos correspondientes al módulo de asistencias.
Permite registrar el ingreso y salida de los clientes
al gimnasio.
"""

from django.db import models
from apps.clientes.models import Cliente

# ENUMERACIONES

class EstadoAsistencia(models.TextChoices):
    """
    Estados disponibles para una asistencia.
    """

    REGISTRADA = "REGISTRADA", "Registrada"
    ANULADA = "ANULADA", "Anulada"

# MODELO ASISTENCIA

class Asistencia(models.Model):
    """
    Registra el ingreso y salida
    de un cliente al gimnasio.
    """

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="asistencias",
        verbose_name="Cliente"
    )

    fecha = models.DateField(
        verbose_name="Fecha"
    )

    hora_ingreso = models.TimeField(
        verbose_name="Hora de ingreso"
    )

    hora_salida = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de salida"
    )

    estado = models.CharField(
        max_length=15,
        choices=EstadoAsistencia.choices,
        default=EstadoAsistencia.REGISTRADA,
        verbose_name="Estado"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ["-fecha", "-hora_ingreso"]

    def __str__(self):
        return f"{self.cliente} - {self.fecha}"