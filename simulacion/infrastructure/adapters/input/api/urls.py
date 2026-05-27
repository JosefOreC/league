from django.urls import path

from .views import get_simulation_context

urlpatterns = [
    # HU-SIM-01 — Contexto de simulación del torneo
    path(
        'torneo/<str:tournament_id>/contexto/',
        get_simulation_context,
        name='simulacion-contexto',
    ),
]
