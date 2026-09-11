"""
Proyecto: AuraFit
Curso: Lenguajes de Programación
Autor: Fernando Jose Concha Jimenez

Descripción:
Este archivo define el modelo Entrenador, que almacena la información
personal y laboral de los entrenadores del gimnasio.
"""

from django.db import models


class Estado(models.TextChoices):
    """
    Estados permitidos para un entrenador.
    """
    ACTIVO = "ACTIVO", "Activo"
    INACTIVO = "INACTIVO", "Inactivo"


class Entrenador(models.Model):
    """
    Modelo que representa a un entrenador del gimnasio.
    """

    nombres = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )

    apellido_paterno = models.CharField(
        max_length=100,
        verbose_name="Apellido paterno"
    )

    apellido_materno = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Apellido materno"
    )

    telefono = models.CharField(
        max_length=20,
        verbose_name="Telefono"
    )

    especialidad = models.CharField(
        max_length=100,
        verbose_name="Especialidad"
    )

    fecha_contratacion = models.DateField(
        verbose_name="Fecha de contratacion"
    )

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        verbose_name="Estado"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creacion"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualizacion"
    )

    class Meta:
        verbose_name = "Entrenador"
        verbose_name_plural = "Entrenadores"
        ordering = [
            "apellido_paterno",
            "apellido_materno",
            "nombres",
        ]

    def __str__(self):
        nombre_completo = " ".join(
            parte for parte in [
                self.nombres,
                self.apellido_paterno,
                self.apellido_materno,
            ] if parte
        )
        return nombre_completo