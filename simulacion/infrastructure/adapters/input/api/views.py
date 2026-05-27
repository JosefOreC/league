"""
Vistas del módulo de simulación — infraestructura de entrada (API REST).

Cada vista:
  - Exige autenticación JWT mediante @auth_required.
  - Delega la lógica de negocio al caso de uso correspondiente.
  - Convierte las excepciones de dominio en respuestas HTTP.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.infrastructure.security.auth_decorator import auth_required

from simulacion.application.use_cases.get_simulation_context_use_case import (
    GetSimulationContextUseCase,
    TeamNotApprovedError,
    TournamentNotFoundError,
)
from simulacion.infrastructure.repositories.tournament_context_repository import (
    TournamentContextRepository,
)


# ---------------------------------------------------------------------------
# HU-SIM-01 — GET /api/simulacion/torneo/<tournament_id>/contexto/
# ---------------------------------------------------------------------------

@api_view(['GET'])
@auth_required([SystemRol.PARTICIPANT])
def get_simulation_context(request: Request, tournament_id: str) -> Response:
    """
    Retorna el contexto de simulación (torneo + equipo + criterios) para el
    líder de equipo autenticado.

    Roles: PARTICIPANT (líder / representante de equipo)
    Auth:  Bearer JWT obligatorio

    Respuestas:
        200 — SimulationContext serializado.
        401 — JWT ausente o inválido (gestionado por @auth_required).
        403 — Representante sin equipo aprobado en el torneo.
        404 — Torneo no encontrado.
    """
    # El auth_decorator inyecta el payload del JWT en request.user_data
    representante_id: str = request.user_data.get('user_id')

    repository = TournamentContextRepository()
    use_case = GetSimulationContextUseCase(tournament_context_port=repository)

    try:
        context = use_case.execute(
            tournament_id=tournament_id,
            representante_id=representante_id,
        )
    except TournamentNotFoundError:
        return Response(
            {'error': 'Torneo no encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )
    except TeamNotApprovedError:
        return Response(
            {'error': 'No tiene un equipo aprobado en este torneo'},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Serialización manual — evita acoplamiento a DRF ModelSerializer
    payload = {
        'tournament': {
            'id': context.tournament.id,
            'name': context.tournament.name,
            'state': context.tournament.state,
            'category': context.tournament.category,
        },
        'team': {
            'id': context.team.id,
            'name': context.team.name,
            'nivel_tecnico_declarado': context.team.nivel_tecnico_declarado,
            'participants_count': context.team.participants_count,
        },
        'criterios': [
            {
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'peso': c.peso,
                'min_qualification': c.min_qualification,
                'max_qualification': c.max_qualification,
            }
            for c in context.criterios
        ],
    }

    return Response(payload, status=status.HTTP_200_OK)
