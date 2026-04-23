from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from ....application.use_cases.create_tournament_use_case import CreateTournamentUseCase
from ....infrastructure.repositories.postgresql_repository.tournament_repository import TournamentRepositoryPostgresql
from ....domain.entities.user import User
from ....domain.value_objects.enums.system_rol import SystemRol
from ....domain.value_objects.enums.user_state import UserState
from ....domain.value_objects.enums.tournament_category import TournamentCategory


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
            {
                "id":              tournament.id,
                "name":            tournament.name,
                "description":     tournament.description,
                "date_start":      tournament.date_start.isoformat(),
                "date_end":        tournament.date_end.isoformat(),
                "state":           tournament.state.value,
                "category":        tournament.category.value,
                "creator_user_id": tournament.creator_user_id,
                "tournament_rule": {
                    "id":          tournament.tournament_rule.id,
                    "min_members": tournament.tournament_rule.min_members,
                    "max_members": tournament.tournament_rule.max_members,
                    "min_teams":   tournament.tournament_rule.min_teams,
                    "max_teams":   tournament.tournament_rule.max_teams,
                    "access_type": tournament.tournament_rule.access_type.value,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )