from django.db import models

from apps.clientes.models import Cliente
from apps.entrenadores.models import Entrenador

# ENUMERACIÓN ESTADO EVALUACIÓN

class EstadoEvaluacion(models.TextChoices):
    """
    Estados disponibles para una evaluación física.
    """

    ACTIVA = "ACTIVA", "Activa"
    ANULADA = "ANULADA", "Anulada"


# MODELO EVALUACIÓN FÍSICA

class EvaluacionFisica(models.Model):
    """
    Registra la evolución física de un cliente.
    """

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        verbose_name="Cliente"
    )

    entrenador = models.ForeignKey(
        Entrenador,
        on_delete=models.CASCADE,
        verbose_name="Entrenador"
    )

    fecha = models.DateField(
        verbose_name="Fecha"
    )

    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Peso (kg)"
    )

    estatura = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name="Estatura (m)"
    )

    porcentaje_grasa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Porcentaje de grasa"
    )

    masa_muscular = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Masa muscular (kg)"
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )

    estado = models.CharField(
        max_length=10,
        choices=EstadoEvaluacion.choices,
        default=EstadoEvaluacion.ACTIVA,
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
        verbose_name = "Evaluación física"
        verbose_name_plural = "Evaluaciones físicas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.cliente} - {self.entrenador} - {self.fecha}"