from django.urls import path

from .views import get_simulation_context, run_simulation

urlpatterns = [
    # HU-SIM-01 — Contexto de simulación del torneo
    path(
        'torneo/<str:tournament_id>/contexto/',
        get_simulation_context,
        name='simulacion-contexto',
    ),
    # HU-SIM-02/03/04/05 — Ejecutar simulación predictiva
    path(
        'torneo/<str:tournament_id>/ejecutar/',
        run_simulation,
        name='simulacion-ejecutar',
    ),
]
