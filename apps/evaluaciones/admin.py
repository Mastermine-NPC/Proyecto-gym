from django.contrib import admin

from .models import EvaluacionFisica


@admin.register(EvaluacionFisica)
class EvaluacionFisicaAdmin(admin.ModelAdmin):
    """
    Configuración del modelo Evaluación Física
    en el panel de administración.
    """

    list_display = (
        "cliente",
        "entrenador",
        "fecha",
        "peso",
        "estado",
    )

    search_fields = (
        "cliente__nombres",
        "cliente__apellido_paterno",
        "cliente__dni",
        "entrenador__nombres",
        "entrenador__apellido_paterno",
    )

    list_filter = (
        "estado",
        "fecha",
    )

    ordering = (
        "-fecha",
    )