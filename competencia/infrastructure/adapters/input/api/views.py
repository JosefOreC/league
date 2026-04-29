# ---------------------------------------------------------------------------
# IMPORTS CORREGIDOS
# ---------------------------------------------------------------------------

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .....application.use_cases.create_tournament_use_case import CreateTournamentUseCase
from .....application.use_cases.config_tournament_rule_use_case import ConfigTournamentRuleUseCase
from .....infrastructure.repositories.postgresql_repository.tournament_repository import TournamentRepositoryPostgresql

from .....domain.entities.criteria import Criteria
from .....domain.entities.tournament_rule import TournamentRule

from .....domain.entities.user import User
from authentication.domain.value_objects.enum.system_rol import SystemRol

from .....domain.value_objects.enums.tournament_category import TournamentCategory
from .....domain.value_objects.enums.tournament_access_type import TournamentAccessType

from authentication.infrastructure.security.auth_decorator import auth_required
from .....application.services.user_compentencia_service import UserCompentenciaService


user_compentencia_service = UserCompentenciaService()

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _parse_datetime(value: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"El campo '{field_name}' debe ser una fecha ISO 8601 válida"
        )


def _parse_criterias(raw: list) -> list[Criteria]:
    result = []

    for i, item in enumerate(raw):

        if not isinstance(item, dict):
            raise ValueError(
                f"El criterio #{i + 1} debe ser un objeto JSON."
            )

        try:
            criteria = Criteria.create(
                name=item["name"],
                description=item.get("description", ""),
                value=float(item["value"]),
            )

        except KeyError as e:
            raise ValueError(
                f"El criterio #{i + 1} le falta el campo: {e}"
            )

        result.append(criteria)

    return result


@api_view(['POST'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def create_tournament(request):

    data = request.data

    required_fields = [
        "name",
        "description",
        "date_start",
        "date_end",
        "category",
        "max_teams"
    ]

    missing = [f for f in required_fields if f not in data]

    if missing:
        return Response(
            {
                "error": f"Faltan los siguientes campos: {', '.join(missing)}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_data = getattr(request, "user_data", {})
        user = user_compentencia_service.dict_to_user(user_data)

        name = str(data["name"]).strip()
        description = str(data["description"]).strip()
        date_start = _parse_datetime(data["date_start"], "date_start")
        date_end = _parse_datetime(data["date_end"], "date_end")
        max_teams = int(data["max_teams"])

        try:
            category = TournamentCategory(data["category"])

        except ValueError:
            valid = [c.value for c in TournamentCategory]

            return Response(
                {
                    "error": f"Categoría inválida. Valores permitidos: {valid}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        repository = TournamentRepositoryPostgresql()

        use_case = CreateTournamentUseCase(
            user=user,
            tournament_repository=repository
        )

        tournament = use_case.execute(
            name=name,
            description=description,
            date_start=date_start,
            date_end=date_end,
            category=category,
            max_teams=max_teams,
        )

        return Response(
            tournament.to_dict(),
            status=status.HTTP_201_CREATED,
        )

    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {
                "error": "Error interno del servidor",
                "detail": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@api_view(['GET'])
@auth_required()
def get_tournament_by_id(request, tournament_id: str):
    try:
        repository = TournamentRepositoryPostgresql()

        tournament = repository.find_by_id(tournament_id)
        
        if not tournament:
            return Response(
                {
                    "error": f"Torneo '{tournament_id}' no encontrado"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            tournament.to_dict(),
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "error": "Error interno del servidor",
                "detail": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@auth_required([SystemRol.ADMIN])
def get_all_tournaments(request):

    try:
        repository = TournamentRepositoryPostgresql()

        tournaments = repository.find_all()

        return Response(
            [t.to_dict() for t in tournaments],
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "error": "Error interno del servidor",
                "detail": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['PUT'])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def config_tournament_rules(request, tournament_id: str):

    data = request.data

    required_fields = [
        "min_members",
        "max_members",
        "min_teams",
        "max_teams",
        "access_type"
    ]

    missing = [f for f in required_fields if f not in data]

    if missing:
        return Response(
            {
                "error": f"Faltan los siguientes campos: {', '.join(missing)}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_data = getattr(request, "user_data", {})
        
        user = user_compentencia_service.dict_to_user(user_data)

        try:
            access_type = TournamentAccessType(data["access_type"])

        except ValueError:
            valid = [a.value for a in TournamentAccessType]

            return Response(
                {
                    "error": f"access_type inválido. Valores permitidos: {valid}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        validation_list = data.get("validation_list", [])

        if not isinstance(validation_list, list):
            return Response(
                {
                    "error": "validation_list debe ser una lista de IDs"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_criterias = data.get("criterias", [])

        if not isinstance(raw_criterias, list):
            return Response(
                {
                    "error": "criterias debe ser una lista de objetos"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        criterias = _parse_criterias(raw_criterias)

        new_rule = TournamentRule.create(
            min_members=int(data["min_members"]),
            max_members=int(data["max_members"]),
            min_teams=int(data["min_teams"]),
            max_teams=int(data["max_teams"]),
            access_type=access_type,
            validation_list=validation_list,
            criterias=criterias,
        )

        repository = TournamentRepositoryPostgresql()

        use_case = ConfigTournamentRuleUseCase(
            tournament_repository=repository,
            user=user,
        )

        tournament = use_case.execute(
            tournament_rule=new_rule,
            tournament_id=tournament_id,
        )

        return Response(
            tournament.to_dict(),
            status=status.HTTP_200_OK
        )

    except PermissionError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_403_FORBIDDEN
        )

    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {
                "error": "Error interno del servidor",
                "detail": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )