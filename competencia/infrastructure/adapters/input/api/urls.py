from django.urls import path
from .views import (
    create_tournament,
    get_tournament_by_id,
    get_all_tournaments,
    config_tournament_rules,
    review_tournament,
    open_registrations,
    close_registrations,
    start_tournament,
    cancel_tournament,
    inscribe_team,
    generate_fixtures,
    register_match_result,
    get_standings,
    draft_tournament
)

urlpatterns = [
    path('all/',                            get_all_tournaments),
    path('create/',                         create_tournament),
    path('torneo/<str:tournament_id>/',     get_tournament_by_id),
    path('torneo/<str:tournament_id>/rules/', config_tournament_rules),
    path('torneo/<str:tournament_id>/review/', review_tournament),
    path('torneo/<str:tournament_id>/open-registrations/', open_registrations),
    path('torneo/<str:tournament_id>/close-registrations/', close_registrations),
    path('torneo/<str:tournament_id>/start/', start_tournament),
    path('torneo/<str:tournament_id>/cancel/', cancel_tournament),
    path('torneo/<str:tournament_id>/inscribir/', inscribe_team),
    path('torneo/<str:tournament_id>/generar-fixtures/', generate_fixtures),
    path('partido/<str:match_id>/resultado/', register_match_result),
    path('torneo/<str:tournament_id>/posiciones/', get_standings),
    path('torneo/<str:tournament_id>/draft/', draft_tournament),
]
