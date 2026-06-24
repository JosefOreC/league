from django.urls import path
from .analisis_views import (
    get_analisis_integral,
)

urlpatterns = [
    # HU-AN-01: Análisis Integral de Resultados del Torneo
    path(
        "torneos/<str:torneo_id>/analisis-integral/",
        get_analisis_integral,
        name="analisis-integral",
    ),
]
