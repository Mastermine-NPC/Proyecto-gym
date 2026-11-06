from django.urls import path
from .views import (
    inscribir_cliente,
    estadisticas_clientes,
    api_orden_inscripciones,
    auditoria_concurrencia_view,
)

app_name = "clientes"

urlpatterns = [
    path("inscribir/", inscribir_cliente, name="inscribir_cliente"),
    path("estadisticas/", estadisticas_clientes, name="estadisticas_clientes"),
    path("orden-inscripciones/", api_orden_inscripciones, name="api_orden_inscripciones"),
    path("auditoria/", auditoria_concurrencia_view, name="auditoria_concurrencia"),
]
