from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from apps.clientes.views import auditoria_concurrencia_view

urlpatterns = [
    path("", RedirectView.as_view(url="/auditoria/", permanent=False)),
    path("auditoria/", auditoria_concurrencia_view, name="auditoria"),
    path("admin/", admin.site.urls),
    path("api/clientes/", include("apps.clientes.urls")),
]