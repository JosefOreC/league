from django.urls import path
from .ia_views import analizar_torneo

urlpatterns = [
    path("analizar", analizar_torneo, name="ia_analizar_torneo"),
]
