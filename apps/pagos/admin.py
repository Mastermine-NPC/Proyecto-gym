from django.contrib import admin
from .models import MetodoPago, Pago

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "estado",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "estado",
    )

    ordering = (
        "nombre",
    )


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "membresia",
        "metodo_pago",
        "monto",
        "fecha_pago",
        "estado",
    )

    search_fields = (
        "membresia__cliente__nombres",
        "membresia__cliente__apellido_paterno",
    )

    list_filter = (
        "estado",
        "metodo_pago",
    )

    ordering = (
        "-fecha_pago",
    )