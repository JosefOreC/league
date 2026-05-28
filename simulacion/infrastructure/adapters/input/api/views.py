"""
Vistas del módulo de simulación — infraestructura de entrada (API REST).

Endpoints implementados:
  GET  /api/simulacion/torneo/<tournament_id>/contexto/   → HU-SIM-01
  POST /api/simulacion/torneo/<tournament_id>/ejecutar/   → HU-SIM-02,03,04,05
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
from simulacion.application.use_cases.run_simulation_use_case import (
    EntregableAusenteError,
    EntregableDemasiadoCortoError,
    RunSimulationUseCase,
)
from simulacion.infrastructure.repositories.tournament_context_repository import (
    TournamentContextRepository,
)
from simulacion.infrastructure.scoring.heuristic_scoring_engine import (
    HeuristicScoringEngine,
)


# ---------------------------------------------------------------------------
# HU-SIM-01 — GET /api/simulacion/torneo/<tournament_id>/contexto/
# ---------------------------------------------------------------------------

@api_view(['GET'])
@auth_required([SystemRol.PARTICIPANT])
def get_simulation_context(request: Request, tournament_id: str) -> Response:
    """
    Retorna el contexto de simulación (torneo + equipo + criterios).
    Roles: PARTICIPANT | Auth: Bearer JWT obligatorio
    """
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


# ---------------------------------------------------------------------------
# HU-SIM-02..05 — POST /api/simulacion/torneo/<tournament_id>/ejecutar/
# ---------------------------------------------------------------------------

@api_view(['POST'])
@auth_required([SystemRol.PARTICIPANT])
def run_simulation(request: Request, tournament_id: str) -> Response:
    """
    Ejecuta la simulación predictiva sobre el entregable textual.

    Body JSON: { "entregable": "<texto de al menos 100 caracteres>" }

    Respuestas:
        200 — SimulationResult completo (scores, puntaje_total, posicion,
              fortalezas, debilidades, retroalimentacion).
        400 — Entregable ausente o demasiado corto.
        401 — JWT inválido (gestionado por @auth_required).
        403 — Sin equipo aprobado / rol insuficiente.
        404 — Torneo no encontrado.
    """
    representante_id: str = request.user_data.get('user_id')
    entregable = request.data.get('entregable')

    repository = TournamentContextRepository()
    engine = HeuristicScoringEngine()
    use_case = RunSimulationUseCase(
        tournament_context_port=repository,
        scoring_engine_port=engine,
    )

    try:
        result = use_case.execute(
            tournament_id=tournament_id,
            representante_id=representante_id,
            entregable=entregable,
        )
    except EntregableAusenteError:
        return Response(
            {'campo': 'entregable', 'error': 'requerido'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except EntregableDemasiadoCortoError as exc:
        return Response(
            {
                'error': 'El entregable debe tener al menos 100 caracteres',
                'actual_length': exc.actual_length,
            },
            status=status.HTTP_400_BAD_REQUEST,
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

    # Serialización manual del SimulationResult
    payload = {
        'simulation_id': result.simulation_id,
        'scores': [
            {
                'criterio_id': s.criterio_id,
                'nombre': s.nombre,
                'peso': s.peso,
                'valor_simulado': s.valor_simulado,
                'valor_normalizado': s.valor_normalizado,
                'en_rango': s.en_rango,
            }
            for s in result.scores
        ],
        'puntaje_total': result.puntaje_total,
        'posicion_estimada': {
            'posicion_estimada': result.posicion.posicion_estimada,
            'total_equipos': result.posicion.total_equipos,
            'percentil': result.posicion.percentil,
            **(
                {'advertencia': result.posicion.advertencia}
                if result.posicion.advertencia
                else {}
            ),
        },
        'fortalezas': [
            {
                'criterio_id': f.criterio_id,
                'nombre': f.nombre,
                'valor_normalizado': f.valor_normalizado,
                'motivo': f.motivo,
            }
            for f in result.fortalezas
        ],
        'debilidades': [
            {
                'criterio_id': d.criterio_id,
                'nombre': d.nombre,
                'valor_normalizado': d.valor_normalizado,
                'motivo': d.motivo,
            }
            for d in result.debilidades
        ],
        'retroalimentacion': {
            'resumen': result.retroalimentacion.resumen,
            'recomendaciones': list(result.retroalimentacion.recomendaciones),
            'sin_mejoras_criticas': result.retroalimentacion.sin_mejoras_criticas,
        },
    }

    return Response(payload, status=status.HTTP_200_OK)
