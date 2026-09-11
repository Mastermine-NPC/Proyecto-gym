"""
Proyecto: AuraFit
Curso: Lenguajes de Programación
Autor: Fernando Jose Concha Jimenez

Descripción:
Este archivo define los modelos TipoMembresia y Membresia.
"""

from django.db import models
from apps.clientes.models import Cliente


class EstadoTipoMembresia(models.TextChoices):
    """
    Estados disponibles para un tipo de membresía.
    """
    ACTIVO = "ACTIVO", "Activo"
    INACTIVO = "INACTIVO", "Inactivo"


class EstadoMembresia(models.TextChoices):
    """
    Estados disponibles para una membresía.
    """
    ACTIVA = "ACTIVA", "Activa"
    VENCIDA = "VENCIDA", "Vencida"
    CANCELADA = "CANCELADA", "Cancelada"


class TipoMembresia(models.Model):
    """
    Catálogo de tipos de membresía.
    """

    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre"
    )

    precio = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Precio"
    )

    duracion_dias = models.PositiveIntegerField(
        verbose_name="Duración (días)"
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )

    estado = models.CharField(
        max_length=10,
        choices=EstadoTipoMembresia.choices,
        default=EstadoTipoMembresia.ACTIVO,
        verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Tipo de membresía"
        verbose_name_plural = "Tipos de membresía"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Membresia(models.Model):
    """
    Membresía adquirida por un cliente.
    """

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="membresias",
        verbose_name="Cliente"
    )

    tipo_membresia = models.ForeignKey(
        TipoMembresia,
        on_delete=models.PROTECT,
        related_name="membresias",
        verbose_name="Tipo de membresía"
    )

    fecha_inicio = models.DateField(
        verbose_name="Fecha de inicio"
    )

    fecha_fin = models.DateField(
        verbose_name="Fecha de fin"
    )

    motivo_cancelacion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motivo de cancelación"
    )

    estado = models.CharField(
        max_length=10,
        choices=EstadoMembresia.choices,
        default=EstadoMembresia.ACTIVA,
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
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.cliente} - {self.tipo_membresia}"