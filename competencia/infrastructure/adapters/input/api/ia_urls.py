from django.urls import path
from .ia_views import analizar_torneo, generar_criterios, actualizar_peso_criterio, confirmar_criterios

urlpatterns = [
    # HU-IA-01
    path("analizar",                                    analizar_torneo,          name="ia_analizar_torneo"),
    # HU-IA-05
    path("generar-criterios",                           generar_criterios,        name="ia_generar_criterios"),
    path("criterios/<str:criterio_id>",                 actualizar_peso_criterio, name="ia_actualizar_peso"),
    path("criterios/<str:sesion_ia_id>/confirmar",      confirmar_criterios,      name="ia_confirmar_criterios"),
]
