from django.urls import path
from .views import (
    create_tournament,
    get_tournament_by_id,
    get_all_tournaments,
    config_tournament_rules,
)

urlpatterns = [
    path('',                             get_all_tournaments),          # GET  /competencia/
    path('create/',                      create_tournament),             # POST /competencia/create/
    path('torneo/<str:tournament_id>/',         get_tournament_by_id),          # GET  /competencia/torneo/<id>/
    path('torneo<str:tournament_id>/rules/',   config_tournament_rules),       # PUT  /competencia/torneo/<id>/rules/
]
