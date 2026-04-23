from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timezone
from uuid import uuid4
from ....application.use_cases.create_tournament_use_case import CreateTournamentUseCase
from ....application.use_cases.config_tournament_rule_use_case import ConfigTournamentRuleUseCase
from ....infrastructure.repositories.postgresql_repository.tournament_repository import TournamentRepositoryPostgresql
from ....domain.entities.user import User
from ....domain.entities.criteria import Criteria
from ....domain.entities.tournament_rule import TournamentRule
from ....domain.value_objects.enums.system_rol import SystemRol
from ....domain.value_objects.enums.user_state import UserState
from ....domain.value_objects.enums.tournament_category import TournamentCategory
from ....domain.value_objects.enums.tournament_access_type import TournamentAccessType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_datetime(value: str, field_name: str) -> datetime:
    """Convierte un string ISO 8601 a datetime. Lanza ValueError si es inválido."""
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f"El campo '{field_name}' debe ser una fecha ISO 8601 válida (ej: 2026-06-01T00:00:00)")


def _build_user_from_request(request) -> User:
    """
    Construye un User de dominio a partir de headers del request.
    Por ahora se usan headers simulados; aquí se integrará el sistema de auth real.

    Cabeceras esperadas:
        X-User-Id     — ID del usuario autenticado
        X-User-Rol    — valor del enum SystemRol  (ej: 'admin')
        X-User-State  — valor del enum UserState  (ej: 'active')
        X-User-Name   — nombre del usuario
        X-User-Email  — email del usuario
    """
    user_id    = request.headers.get("X-User-Id")
    user_rol   = request.headers.get("X-User-Rol")
    user_state = request.headers.get("X-User-State")
    user_name  = request.headers.get("X-User-Name", "")
    user_email = request.headers.get("X-User-Email", "")

    if not all([user_id, user_rol, user_state]):
        raise PermissionError(
            "Faltan las cabeceras de autenticación: X-User-Id, X-User-Rol, X-User-State"
        )

    try:
        rol   = SystemRol(user_rol)
        state = UserState(user_state)
    except ValueError:
        raise PermissionError(
            f"Rol o estado de usuario inválido: rol='{user_rol}', state='{user_state}'"
        )

    return User(
        id=user_id,
        name=user_name,
        email=user_email,
        date_registered=datetime.now(),
        birth_date=datetime(2000, 1, 1),  # placeholder — falta sustituir con auth real
        rol=rol,
        state=state,
    )


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------

@api_view(['POST'])
def create_tournament(request):
    """
    POST /competencia/create/

    Body JSON:
    {
        "name":        "Torneo Nacional",
        "description": "Descripción del torneo",
        "date_start":  "2026-06-01T09:00:00",
        "date_end":    "2026-06-30T18:00:00",
        "category":    "explorador" | "constructor" | "innovador",
        "max_teams":   16
    }

    Headers requeridos (auth temporal):
        X-User-Id, X-User-Rol, X-User-State, X-User-Name, X-User-Email
    """
    # 1. Autenticación del usuario desde headers
    # try:
    #     user = _build_user_from_request(request)
    # except PermissionError as e:
    #     return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    # 2. Validación de campos requeridos en el body
    data = request.data
    required_fields = ["name", "description", "date_start", "date_end", "category", "max_teams"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return Response(
            {"error": f"Faltan los siguientes campos: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # 3. Parseo y conversión de tipos
        name        = str(data["name"]).strip()
        description = str(data["description"]).strip()
        date_start  = _parse_datetime(data["date_start"], "date_start")
        date_end    = _parse_datetime(data["date_end"],   "date_end")
        max_teams   = int(data["max_teams"])

        try:
            category = TournamentCategory(data["category"])
        except ValueError:
            valid = [c.value for c in TournamentCategory]
            return Response(
                {"error": f"Categoría inválida. Valores permitidos: {valid}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4. Instanciar repositorio y use case
        ### FOR TEST BEFORE IMPLEMENT AUTH
        user = User(
            id="1",
            name="Test",
            email="[EMAIL_ADDRESS]",
            date_registered=datetime.now(),
            birth_date=datetime(2000, 1, 1),
            rol=SystemRol.ADMIN,
            state=UserState.ACTIVE,
        )
        repository = TournamentRepositoryPostgresql()
        use_case   = CreateTournamentUseCase(user=user, tournament_repository=repository)

        # 5. Ejecutar caso de uso
        tournament = use_case.execute(
            name=name,
            description=description,
            date_start=date_start,
            date_end=date_end,
            category=category,
            max_teams=max_teams,
        )

        # 6. Serializar y retornar respuesta
        return Response(
            tournament.to_dict(),
            status=status.HTTP_201_CREATED,
        )

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ---------------------------------------------------------------------------
# Helper: parseo de criterias del request
# ---------------------------------------------------------------------------

def _parse_criterias(raw: list) -> list[Criteria]:
    """
    Convierte la lista de criterias del request (dicts) a objetos Criteria de dominio.
    Formato esperado de cada elemento:
        {"name": "Creatividad", "description": "...", "value": 0.4}
    """
    result = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"El criterio #{i + 1} debe ser un objeto JSON.")
        try:
            c = Criteria.create(
                name=item["name"],
                description=item.get("description", ""),
                value=float(item["value"]),
            )
        except KeyError as e:
            raise ValueError(f"El criterio #{i + 1} le falta el campo: {e}")
        result.append(c)
    return result


# ---------------------------------------------------------------------------
# Views adicionales
# ---------------------------------------------------------------------------

@api_view(['GET'])
def get_tournament_by_id(request, tournament_id: str):
    """
    GET /competencia/<tournament_id>/
    """
    try:
        repository = TournamentRepositoryPostgresql()
        tournament = repository.find_by_id(tournament_id)
        if not tournament:
            return Response(
                {"error": f"Torneo '{tournament_id}' no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(tournament.to_dict(), status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
def get_all_tournaments(request):
    """
    GET /competencia/
    """
    try:
        repository  = TournamentRepositoryPostgresql()
        tournaments = repository.find_all()
        return Response(
            [t.to_dict() for t in tournaments],
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['PUT'])
def config_tournament_rules(request, tournament_id: str):
    """
    PUT /competencia/<tournament_id>/rules/

    Configura las reglas de un torneo en estado DRAFT.
    Solo el MANAGER del torneo puede hacerlo.

    Body JSON:
    {
        "min_members":    2,
        "max_members":    5,
        "min_teams":      4,
        "max_teams":      16,
        "access_type":    "public" | "private",
        "validation_list": ["inst-id-1"],          # solo si private
        "criterias": [
            {"name": "Creatividad", "description": "...", "value": 0.4},
            {"name": "Innovacion",  "description": "...", "value": 0.6}
        ]
    }
    """
    data = request.data

    # 1. Validar campos requeridos
    required_fields = ["min_members", "max_members", "min_teams", "max_teams", "access_type"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return Response(
            {"error": f"Faltan los siguientes campos: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # 2. Convertir access_type
        try:
            access_type = TournamentAccessType(data["access_type"])
        except ValueError:
            valid = [a.value for a in TournamentAccessType]
            return Response(
                {"error": f"access_type inválido. Valores permitidos: {valid}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Parsear listas opcionales
        validation_list = data.get("validation_list", [])
        if not isinstance(validation_list, list):
            return Response(
                {"error": "validation_list debe ser una lista de IDs de institución"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_criterias = data.get("criterias", [])
        if not isinstance(raw_criterias, list):
            return Response(
                {"error": "criterias debe ser una lista de objetos"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        criterias = _parse_criterias(raw_criterias)

        # 4. Construir la nueva TournamentRule de dominio
        new_rule = TournamentRule.create(
            min_members=int(data["min_members"]),
            max_members=int(data["max_members"]),
            min_teams=int(data["min_teams"]),
            max_teams=int(data["max_teams"]),
            access_type=access_type,
            validation_list=validation_list,
            criterias=criterias,
        )

        # 5. Auth (temporal) — sustituir por auth real
        ### FOR TEST BEFORE IMPLEMENT AUTH
        user = User(
            id="1",
            name="Test",
            email="test@test.com",
            date_registered=datetime.now(),
            birth_date=datetime(2000, 1, 1),
            rol=SystemRol.ADMIN,
            state=UserState.ACTIVE,
        )

        # 6. Ejecutar use case
        repository = TournamentRepositoryPostgresql()
        use_case   = ConfigTournamentRuleUseCase(
            tournament_repository=repository,
            user=user,
        )
        tournament = use_case.execute(
            tournament_rule=new_rule,
            tournament_id=tournament_id,
        )

        return Response(tournament.to_dict(), status=status.HTTP_200_OK)

    except PermissionError as e:
        return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
