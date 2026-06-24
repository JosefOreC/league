from django.urls import path
from .analisis_views import (
    get_analisis_integral,
    get_reporte_individual,
    get_tablero_inteligencia,
    get_panel_docente,
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
    # HU-AN-04: Tablero de Inteligencia para el Organizador
    path(
        "torneos/<str:torneo_id>/tablero-inteligencia/",
        get_tablero_inteligencia,
        name="tablero-inteligencia",
    ),
    # HU-AN-08: Panel de Retroalimentación para Docentes
    path(
        "torneos/<str:torneo_id>/equipos/<str:equipo_id>/panel-docente/",
        get_panel_docente,
        name="panel-docente",
    ),
]
