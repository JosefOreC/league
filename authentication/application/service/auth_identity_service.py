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
    def __init__(self, user_repository: UserRepository):
        self.__user_repository = user_repository

    def build_user_from_payload(self, payload: dict) -> User:
        try:
            user = self.__user_repository.get_by_id(payload["user_id"])
            if not user:
                raise ValueError("El usuario no existe.")
            return user

        except KeyError as e:
            raise ValueError(
                f"Payload JWT incompleto. Falta el campo requerido: {e}"
            )

        except ValueError as e:
            raise ValueError(
                f"Datos inválidos en payload JWT: {str(e)}"
            )