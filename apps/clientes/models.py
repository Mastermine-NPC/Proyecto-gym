# Prueba de Git - AuraFit

from django.db import models


class Sexo(models.TextChoices):
    """
    Opciones permitidas para el sexo del cliente.
    """
    MASCULINO = "M", "Masculino"
    FEMENINO = "F", "Femenino"


class Estado(models.TextChoices):
    """
    Estados permitidos para un cliente.
    """
    ACTIVO = "ACTIVO", "Activo"
    INACTIVO = "INACTIVO", "Inactivo"


class Cliente(models.Model):
    """
    Modelo que representa a un cliente del gimnasio.
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

    dni = models.CharField(
        max_length=8,
        unique=True,
        verbose_name="DNI"
    )

    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono"
    )

    correo = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico"
    )

    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de nacimiento"
    )

    sexo = models.CharField(
        max_length=1,
        choices=Sexo.choices,
        verbose_name="Sexo"
    )

    direccion = models.CharField(
        max_length=200,
        verbose_name="Dirección"
    )

    fecha_registro = models.DateField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
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
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
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