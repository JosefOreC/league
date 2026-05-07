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
from .....application.use_cases.qualify_match_use_case import QualifyMatchUseCase
from .....application.use_cases.calculate_standings_use_case import CalculateStandingsUseCase
from .....application.use_cases.approve_team_use_case import ApproveTeamUseCase
from .....application.use_cases.reject_team_use_case import RejectTeamUseCase
from .....application.use_cases.get_teams_by_tournament_use_case import GetTeamsByTournamentUseCase
from .....application.use_cases.get_my_tournaments_use_case import GetMyTournamentsUseCase

from .....infrastructure.repositories.postgresql_repository.tournament_repository import TournamentRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.team_repository import TeamRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.match_repository import MatchRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.match_result_repository import MatchResultRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.standing_repository import StandingRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.institution_repository import InstitutionRepositoryPostgresql
from .....infrastructure.repositories.postgresql_repository.docente_asesor_repository import DocenteAsesorRepositoryPostgresql
from .....application.use_cases.draft_tournament_use_case import DraftTournamentUseCase
from authentication.domain.value_objects.enum.system_rol import SystemRol
from .....domain.value_objects.enums.tournament_category import TournamentCategory
from authentication.infrastructure.security.auth_decorator import auth_required
from .....application.services.user_compentencia_service import UserCompentenciaService

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _parse_datetime(value: str, field_name: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
        # Normalizar a naive: quitar tzinfo si viene con zona horaria
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt
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
            inst_repo = InstitutionRepositoryPostgresql()
            doc_repo = DocenteAsesorRepositoryPostgresql()
            use_case = use_case_class(
                team_repository=team_repo, 
                tournament_repository=repository,
                institution_repository=inst_repo,
                docente_repository=doc_repo
            )
        elif use_case_class == GenerateFixturesUseCase:
            use_case = use_case_class(match_repository=match_repo, tournament_repository=repository, team_repository=team_repo)
        elif use_case_class == RegisterMatchResultUseCase:
            use_case = use_case_class(match_repository=match_repo, match_result_repository=result_repo)
        elif use_case_class == CalculateStandingsUseCase:
            use_case = use_case_class(match_repository=match_repo, standing_repository=standing_repo)
        elif use_case_class in [ApproveTeamUseCase, RejectTeamUseCase, GetTeamsByTournamentUseCase]:
            use_case = use_case_class(team_repository=team_repo)
        elif use_case_class == StartTournamentUseCase:
            use_case = use_case_class(tournament_repository=repository, user=user, team_repository=team_repo)
        elif use_case_class == QualifyMatchUseCase:
            use_case = use_case_class(
                match_repository=match_repo, 
                match_result_repository=result_repo, 
                tournament_repository=repository,
                team_repository=team_repo
            )
        else:
            use_case = use_case_class(tournament_repository=repository, user=user)
        
        if use_case_class == InscribeTeamUseCase:
            kwargs["user"] = user
        
        if use_case_class == QualifyMatchUseCase:
            kwargs["user_id"] = user.id if user else "system"
            
        result = use_case.execute(**kwargs)
        
        if result is None and "tournament_id" in kwargs:
             result = repository.find_by_id(kwargs["tournament_id"])

        if isinstance(result, dict):
            return Response(result, status=status.HTTP_200_OK)

        if isinstance(result, list):
            # Serializar lista de objetos de dominio que tengan to_dict()
            serialized = [
                item.to_dict() if hasattr(item, "to_dict") else item
                for item in result
            ]
            return Response(serialized, status=status.HTTP_200_OK)

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
        category_str = str(data["category"]).lower()
        try:
            category = TournamentCategory(category_str)
        except ValueError:
            # Intentar buscar por nombre si el valor falló
            try:
                category = TournamentCategory[category_str.upper()]
            except KeyError:
                return Response(
                    {"error": f"Categoría '{category_str}' no es válida. Use: explorador, innovador, constructor"},
                    status=status.HTTP_400_BAD_REQUEST
                )
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
def get_tournament_by_id(request, tournament_id: str):
    repository = TournamentRepositoryPostgresql()
    tournament = repository.find_by_id(tournament_id)
    if not tournament:
        return Response({"error": "Torneo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    return Response(tournament.to_dict(), status=status.HTTP_200_OK)

@api_view(['GET'])
@auth_required()
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
def draft_tournament(request, tournament_id: str):
    return _execute_generic_use_case(request, DraftTournamentUseCase, tournament_id=tournament_id)

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
    """HU-GT-06: Registrar resultado con avance de llaves."""
    data = request.data
    return _execute_generic_use_case(
        request, 
        QualifyMatchUseCase, 
        match_id=match_id, 
        qualifications=data.get("qualifications", [])
    )

@api_view(['GET'])
def get_standings(request, tournament_id: str):
    """HU-GT-07: Tabla de posiciones."""
    return _execute_generic_use_case(request, CalculateStandingsUseCase, tournament_id=tournament_id)

@api_view(['GET'])
def get_public_tournament_data(request, tournament_id: str):
    """Pantalla pública del torneo: Datos, Equipos, Fixture, Standings"""
    repository = TournamentRepositoryPostgresql()
    team_repo = TeamRepositoryPostgresql()
    match_repo = MatchRepositoryPostgresql()
    
    try:
        tournament = repository.find_by_id(tournament_id)
        if not tournament:
            return Response({"error": "Torneo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
        teams = team_repo.find_by_tournament(tournament_id)
        matches = match_repo.find_by_tournament(tournament_id)
        
        # We can calculate standings directly or just return the data for the frontend to render
        # Let's call the Use Case for standings
        standings_response = _execute_generic_use_case(request, CalculateStandingsUseCase, tournament_id=tournament_id)
        standings_data = standings_response.data if isinstance(standings_response, Response) and standings_response.status_code == 200 else []
        
        # Obtener resultados de todos los partidos
        all_results = MatchResultRepositoryPostgresql().find_by_tournament(tournament_id)
        results_by_match = {}
        for r in all_results:
            m_id = str(r.match_id)
            if m_id not in results_by_match:
                results_by_match[m_id] = []
            results_by_match[m_id].append(r.to_dict())

        # Debug logs
        print(f"DEBUG: Encontrados {len(all_results)} resultados para el torneo {tournament_id}")
        print(f"DEBUG: Partidos con resultados: {list(results_by_match.keys())}")

        # Determinar ganador si el torneo finalizó
        winner_team = None
        if tournament.state.value == "finalized":
            final_match = next((m for m in matches if not m.partido_siguiente_id and m.ganador_id), None)
            if final_match:
                winner_obj = next((t for t in teams if str(t.id) == str(final_match.ganador_id)), None)
                if winner_obj:
                    winner_team = winner_obj.to_dict()

        return Response({
            "tournament": tournament.to_dict(),
            "teams": [t.to_dict() for t in teams],
            "matches": [
                {**m.to_dict(), "results": results_by_match.get(str(m.id), [])} 
                for m in matches
            ],
            "standings": standings_data,
            "winner": winner_team
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error interno", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def approve_team(request, team_id: str):
    """Aprobar inscripción de un equipo."""
    return _execute_generic_use_case(request, ApproveTeamUseCase, team_id=team_id)

@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def reject_team(request, team_id: str):
    """Rechazar inscripción de un equipo."""
    return _execute_generic_use_case(request, RejectTeamUseCase, team_id=team_id)

@api_view(['GET'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def get_tournament_teams(request, tournament_id: str):
    """Listar todos los equipos inscritos en un torneo para administración."""
    return _execute_generic_use_case(request, GetTeamsByTournamentUseCase, tournament_id=tournament_id)


@api_view(['GET'])
@auth_required()
def get_my_tournaments(request):
    """Torneos en los que el usuario autenticado participa como representante de equipo."""
    try:
        user_data = getattr(request, "user_data", {})
        user = UserCompentenciaService.dict_to_user(user_data)
        if not user or not user.id:
            return Response({"error": "No se pudo identificar al usuario"}, status=status.HTTP_401_UNAUTHORIZED)

        use_case = GetMyTournamentsUseCase(
            team_repository=TeamRepositoryPostgresql(),
            tournament_repository=TournamentRepositoryPostgresql()
        )
        result = use_case.execute(user=user)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
