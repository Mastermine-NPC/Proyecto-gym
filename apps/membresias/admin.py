"""
Proyecto: AuraFit
Curso: Lenguajes de Programación
Autor: Sebastian Chambi Mamani

Descripción:
Registro de los modelos TipoMembresia y Membresia
en el panel de administración de Django.
"""

from django.contrib import admin
from .models import TipoMembresia, Membresia


@admin.register(TipoMembresia)
class TipoMembresiaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "precio",
        "duracion_dias",
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


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "tipo_membresia",
        "fecha_inicio",
        "fecha_fin",
        "estado",
    )

    search_fields = (
        "cliente__nombres",
        "cliente__apellido_paterno",
    )

    list_filter = (
        "estado",
        "tipo_membresia",
    )

    ordering = (
        "-fecha_inicio",
    )