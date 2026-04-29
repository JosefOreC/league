from ...domain.value_objects.enum.system_rol import SystemRol
from ...domain.value_objects.enum.user_state import UserState
from ...domain.entities.user import User
from ...domain.ports.user_repository import UserRepository
from datetime import datetime

class AuthIdentityService:
    """
    Servicio encargado de transformar payload JWT validado
    en entidad de dominio User reutilizable por otros módulos.
    """

    def build_user_from_payload(self, payload: dict) -> User:
        try:
            return User(
                id=payload["user_id"],
                name=payload.get("name", ""),
                email=payload.get("email", ""),
                rol=SystemRol(payload["rol"]),
                state=UserState(payload["state"]),
            )

        except KeyError as e:
            raise ValueError(
                f"Payload JWT incompleto. Falta el campo requerido: {e}"
            )

        except ValueError as e:
            raise ValueError(
                f"Datos inválidos en payload JWT: {str(e)}"
            )