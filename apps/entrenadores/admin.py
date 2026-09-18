from django.contrib import admin
from .models import Entrenador


@admin.register(Entrenador)
class EntrenadorAdmin(admin.ModelAdmin):
    """
    Configuración del modelo Entrenador en el panel de administración.
    """

    list_display = (
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "especialidad",
        "estado",
    )

    search_fields = (
        "nombres",
        "apellido_paterno",
        "apellido_materno",
    )

    list_filter = (
        "estado",
        "especialidad",
    )

    ordering = (
        "apellido_paterno",
        "apellido_materno",
        "nombres",
    )