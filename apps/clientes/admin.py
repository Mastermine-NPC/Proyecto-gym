from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuración del modelo Cliente en el panel de administración.
    """

    list_display = (
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "dni",
        "telefono",
        "correo",
        "estado",
    )

    search_fields = (
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "dni",
    )

    list_filter = (
        "estado",
        "sexo",
    )

    ordering = (
        "apellido_paterno",
        "apellido_materno",
        "nombres",
    )