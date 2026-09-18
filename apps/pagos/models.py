from django.db import models
from apps.membresias.models import Membresia


class EstadoMetodoPago(models.TextChoices):
    """
    Estados disponibles para un método de pago.
    """
    ACTIVO = "ACTIVO", "Activo"
    INACTIVO = "INACTIVO", "Inactivo"


class EstadoPago(models.TextChoices):
    """
    Estados disponibles para un pago.
    """
    PENDIENTE = "PENDIENTE", "Pendiente"
    PAGADO = "PAGADO", "Pagado"
    ANULADO = "ANULADO", "Anulado"


class MetodoPago(models.Model):
    """
    Catálogo de métodos de pago.
    """

    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre"
    )

    estado = models.CharField(
        max_length=10,
        choices=EstadoMetodoPago.choices,
        default=EstadoMetodoPago.ACTIVO,
        verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Método de pago"
        verbose_name_plural = "Métodos de pago"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Pago(models.Model):
    """
    Pago realizado por una membresía.
    """

    membresia = models.ForeignKey(
        Membresia,
        on_delete=models.PROTECT,
        related_name="pagos",
        verbose_name="Membresía"
    )

    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name="pagos",
        verbose_name="Método de pago"
    )

    monto = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Monto"
    )

    fecha_pago = models.DateField(
        verbose_name="Fecha de pago"
    )

    referencia_operacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Referencia de operación"
    )

    estado = models.CharField(
        max_length=10,
        choices=EstadoPago.choices,
        default=EstadoPago.PAGADO,
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
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha_pago"]

    def __str__(self):
        return f"{self.membresia.cliente} - S/. {self.monto}"