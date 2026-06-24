from django.urls import path
from .analisis_views import (
    get_analisis_integral,
    get_reporte_individual,
)

urlpatterns = [
    # HU-AN-01: Análisis Integral de Resultados del Torneo
    path(
        "torneos/<str:torneo_id>/analisis-integral/",
        get_analisis_integral,
        name="analisis-integral",
    ),
    # HU-AN-02: Reporte de Desempeño Individual por Equipo
    path(
        "torneos/<str:torneo_id>/equipos/<str:equipo_id>/reporte-individual/",
        get_reporte_individual,
        name="reporte-individual",
    ),
]
