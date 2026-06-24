from django.urls import path
from .analisis_views import (
    get_analisis_integral,
    get_reporte_individual,
    get_tablero_inteligencia,
    get_panel_docente,
    get_reporte_institucional,
    get_sugerencias,
    generar_certificados,
    generar_resumen_ejecutivo,
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
    # HU-AN-03: Reporte Institucional
    path(
        "instituciones/<str:inst_id>/reporte/",
        get_reporte_institucional,
        name="reporte-institucional",
    ),
    # HU-AN-04: Tablero de Inteligencia para el Organizador
    path(
        "torneos/<str:torneo_id>/tablero-inteligencia/",
        get_tablero_inteligencia,
        name="tablero-inteligencia",
    ),
    # HU-AN-05: Sugerencias inteligentes de acción
    path(
        "torneos/<str:torneo_id>/sugerencias/",
        get_sugerencias,
        name="sugerencias",
    ),
    # HU-AN-06: Certificados y Reconocimientos
    path(
        "torneos/<str:torneo_id>/certificados/",
        generar_certificados,
        name="certificados",
    ),
    # HU-AN-07: Resumen Ejecutivo Automático (NLG)
    path(
        "torneos/<str:torneo_id>/resumen-ejecutivo/",
        generar_resumen_ejecutivo,
        name="resumen-ejecutivo",
    ),
    # HU-AN-08: Panel de Retroalimentación para Docentes
    path(
        "torneos/<str:torneo_id>/equipos/<str:equipo_id>/panel-docente/",
        get_panel_docente,
        name="panel-docente",
    ),
]
