from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .....application.use_cases.create_tournament_use_case import CreateTournamentUseCase
from .....application.use_cases.config_tournament_rule_use_case import ConfigTournamentRuleUseCase
from .....application.use_cases.review_tournament_use_case import ReviewTournamentUseCase
from .....application.use_cases.open_registrations_use_case import OpenRegistrationsUseCase
from .....application.use_cases.close_registrations_use_case import CloseRegistrationsUseCase
from .....application.use_cases.start_tournament_use_case import StartTournamentUseCase
from .....application.use_cases.cancell_tournament_use_case import CancellTournamentUseCase
from .....infrastructure.repositories.postgresql_repository.tournament_repository import TournamentRepositoryPostgresql

from authentication.domain.value_objects.enum.system_rol import SystemRol

from .....domain.value_objects.enums.tournament_category import TournamentCategory

from authentication.infrastructure.security.auth_decorator import auth_required
from .....application.services.user_compentencia_service import UserCompentenciaService


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _parse_datetime(value: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f"El campo '{field_name}' debe ser una fecha ISO 8601 válida")

def _execute_tournament_action(request, use_case_class, **kwargs):
    """Helper genérico para ejecutar casos de uso de acciones sobre torneos."""
    try:
        user_data = getattr(request, "user_data", {})
        user = UserCompentenciaService.dict_to_user(user_data)
        
        repository = TournamentRepositoryPostgresql()
        use_case = use_case_class(tournament_repository=repository, user=user)
        
        result = use_case.execute(**kwargs)
        
        # Si el caso de uso no devuelve el objeto, intentamos recuperarlo por ID
        if result is None and "tournament_id" in kwargs:
             result = repository.find_by_id(kwargs["tournament_id"])

        if result and hasattr(result, "to_dict"):
            return Response(result.to_dict(), status=status.HTTP_200_OK)
        
        return Response({"message": "Acción completada con éxito"}, status=status.HTTP_200_OK)

    except PermissionError as e:
        return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# ---------------------------------------------------------------------------
# VIEWS
# ---------------------------------------------------------------------------

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def create_tournament(request):
    """
    JSON Recibido:
    {
        "name": "string",
        "description": "string",
        "date_start": "2024-12-31T23:59:59",
        "date_end": "2025-01-01T23:59:59",
        "category": "amateur | profesional | etc",
        "max_teams": 16
    }
    """
    data = request.data
    required = ["name", "description", "date_start", "date_end", "category", "max_teams"]
    missing = [f for f in required if f not in data]
    if missing:
        return Response({"error": f"Faltan campos: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_data = getattr(request, "user_data", {})
        user = UserCompentenciaService.dict_to_user(user_data)
        
        category = TournamentCategory(data["category"])
        date_start = _parse_datetime(data["date_start"], "date_start")
        date_end = _parse_datetime(data["date_end"], "date_end")

        repository = TournamentRepositoryPostgresql()
        use_case = CreateTournamentUseCase(user=user, tournament_repository=repository)

        tournament = use_case.execute(
            name=str(data["name"]).strip(),
            description=str(data["description"]).strip(),
            date_start=date_start,
            date_end=date_end,
            category=category,
            max_teams=int(data["max_teams"]),
        )
        return Response(tournament.to_dict(), status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error interno", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@auth_required()
def get_tournament_by_id(request, tournament_id: str):
    repository = TournamentRepositoryPostgresql()
    tournament = repository.find_by_id(tournament_id)
    if not tournament:
        return Response({"error": f"Torneo '{tournament_id}' no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    return Response(tournament.to_dict(), status=status.HTTP_200_OK)


@api_view(['GET'])
@auth_required([SystemRol.ADMIN])
def get_all_tournaments(request):
    repository = TournamentRepositoryPostgresql()
    tournaments = repository.find_all()
    return Response([t.to_dict() for t in tournaments], status=status.HTTP_200_OK)


@api_view(['PUT'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def config_tournament_rules(request, tournament_id: str):
    """Configura las reglas, tipo de torneo y evaluación."""
    data = request.data
    required = ["tournament_rule", "tournament_config", "tournament_evaluation"]
    missing = [f for f in required if f not in data]
    if missing:
        return Response({"error": f"Faltan campos: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

    return _execute_tournament_action(
        request, 
        ConfigTournamentRuleUseCase, 
        tournament_id=tournament_id,
        tournament_rule=data["tournament_rule"],
        tournament_config=data["tournament_config"],
        tournament_evaluation=data["tournament_evaluation"]
    )


@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def review_tournament(request, tournament_id: str):
    return _execute_tournament_action(request, ReviewTournamentUseCase, tournament_id=tournament_id)


@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def open_registrations(request, tournament_id: str):
    return _execute_tournament_action(request, OpenRegistrationsUseCase, tournament_id=tournament_id)


@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def close_registrations(request, tournament_id: str):
    return _execute_tournament_action(request, CloseRegistrationsUseCase, tournament_id=tournament_id)


@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def start_tournament(request, tournament_id: str):
    return _execute_tournament_action(request, StartTournamentUseCase, tournament_id=tournament_id)


@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def cancel_tournament(request, tournament_id: str):
    return _execute_tournament_action(request, CancellTournamentUseCase, tournament_id=tournament_id)