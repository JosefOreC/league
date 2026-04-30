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
from .....application.use_cases.inscribe_team_use_case import InscribeTeamUseCase
from .....application.use_cases.generate_fixtures_use_case import GenerateFixturesUseCase
from .....application.use_cases.register_match_result_use_case import RegisterMatchResultUseCase
from .....application.use_cases.calculate_standings_use_case import CalculateStandingsUseCase

from .....infrastructure.repositories.postgresql_repository.tournament_repository import TournamentRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.team_repository import TeamRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.match_repository import MatchRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.match_result_repository import MatchResultRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.standing_repository import StandingRepositoryPostgresql

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

def _execute_generic_use_case(request, use_case_class, **kwargs):
    """Helper genérico para ejecutar casos de uso con inyección de dependencias básica."""
    try:
        user_data = getattr(request, "user_data", {})
        user = UserCompentenciaService.dict_to_user(user_data)
        
        repository = TournamentRepositoryPostgresql()
        team_repo = TeamRepositoryPostgresql()
        match_repo = MatchRepositoryPostgresql()
        result_repo = MatchResultRepositoryPostgresql()
        standing_repo = StandingRepositoryPostgresql()

        # Inyección manual de dependencias según el caso de uso
        if use_case_class == InscribeTeamUseCase:
            use_case = use_case_class(team_repository=team_repo, tournament_repository=repository)
        elif use_case_class == GenerateFixturesUseCase:
            use_case = use_case_class(match_repository=match_repo, tournament_repository=repository)
        elif use_case_class == RegisterMatchResultUseCase:
            use_case = use_case_class(match_repository=match_repo, match_result_repository=result_repo)
        elif use_case_class == CalculateStandingsUseCase:
            use_case = use_case_class(match_repository=match_repo, standing_repository=standing_repo)
        else:
            use_case = use_case_class(tournament_repository=repository, user=user)
        
        result = use_case.execute(**kwargs)
        
        if result is None and "tournament_id" in kwargs:
             result = repository.find_by_id(kwargs["tournament_id"])

        if isinstance(result, (dict, list)):
            return Response(result, status=status.HTTP_200_OK)
        
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
    data = request.data
    required = ["name", "description", "date_start", "date_end", "category", "max_teams"]
    if any(f not in data for f in required):
        return Response({"error": "Faltan campos obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_data = getattr(request, "user_data", {})
        user = UserCompentenciaService.dict_to_user(user_data)
        category = (data["category"])
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
        return Response({"error": "Torneo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
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
    data = request.data
    return _execute_generic_use_case(
        request, ConfigTournamentRuleUseCase, 
        tournament_id=tournament_id,
        tournament_rule=data.get("tournament_rule"),
        tournament_config=data.get("tournament_config"),
        tournament_evaluation=data.get("tournament_evaluation")
    )

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def review_tournament(request, tournament_id: str):
    return _execute_generic_use_case(request, ReviewTournamentUseCase, tournament_id=tournament_id)

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def open_registrations(request, tournament_id: str):
    return _execute_generic_use_case(request, OpenRegistrationsUseCase, tournament_id=tournament_id)

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def close_registrations(request, tournament_id: str):
    return _execute_generic_use_case(request, CloseRegistrationsUseCase, tournament_id=tournament_id)

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def start_tournament(request, tournament_id: str):
    return _execute_generic_use_case(request, StartTournamentUseCase, tournament_id=tournament_id)

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def cancel_tournament(request, tournament_id: str):
    return _execute_generic_use_case(request, CancellTournamentUseCase, tournament_id=tournament_id)

# NUEVAS HISTORIAS DE USUARIO (HU-GT-04 a HU-GT-07)

@api_view(['POST'])
@auth_required([SystemRol.PARTICIPANT, SystemRol.COACH])
def inscribe_team(request, tournament_id: str):
    """HU-GT-05: Inscribir equipo."""
    data = request.data
    return _execute_generic_use_case(
        request, InscribeTeamUseCase, 
        tournament_id=tournament_id,
        team_data=data.get("team"),
        participants_data=data.get("participants", [])
    )

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def generate_fixtures(request, tournament_id: str):
    """HU-GT-04: Generar fixtures."""
    return _execute_generic_use_case(request, GenerateFixturesUseCase, tournament_id=tournament_id)

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def register_match_result(request, match_id: str):
    """HU-GT-06: Registrar resultado."""
    data = request.data
    return _execute_generic_use_case(request, RegisterMatchResultUseCase, match_id=match_id, results_data=data.get("results", []))

@api_view(['GET'])
@auth_required()
def get_standings(request, tournament_id: str):
    """HU-GT-07: Tabla de posiciones."""
    return _execute_generic_use_case(request, CalculateStandingsUseCase, tournament_id=tournament_id)