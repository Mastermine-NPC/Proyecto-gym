from django.contrib import admin

from .models import Asistencia


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):

    list_display = (
        "cliente",
        "fecha",
        "hora_ingreso",
        "hora_salida",
        "estado",
    )

    search_fields = (
        "cliente__nombres",
        "cliente__apellido_paterno",
        "cliente__dni",
    )

    list_filter = (
        "fecha",
        "estado",
    )

    ordering = (
        "-fecha",
        "-hora_ingreso",
    )