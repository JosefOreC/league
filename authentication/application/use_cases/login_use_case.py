from ...domain.ports.user_repository import UserRepository
from ..service.password_service import PasswordService
from ...domain.entities.user import User
from ..service.jwt_service import JWTService
from datetime import datetime
from zoneinfo import ZoneInfo

class InvalidCredentials(Exception):
    def __init__(self, message):
        super().__init__(message)

class AccountLocked(Exception):
    def __init__(self, message):
        super().__init__(message)


class LoginUseCase:
    def __init__(self, user_repository: UserRepository, password_service: PasswordService, jwt_service: JWTService):
        self.__user_repository = user_repository
        self.__password_service = password_service
        self.__jwt_service = jwt_service

    def execute(self, email: str, password: str) -> dict:
        user = self.__user_repository.get_by_email(email)
        if user is None:
            raise InvalidCredentials("Credenciales Inválidas")
        if user.is_locked():
            raise AccountLocked(f"Cuenta bloqueado, inténtelo de nuevo en {user.time_to_unlock()} minutos")
        if not self.__password_service.verify_password(user, password):
            user.increment_attempts()
            self.__user_repository.update(user)
            raise InvalidCredentials("Credenciales Inválidas")
        
        user.reset_attempts()
        user.update_last_login(datetime.now(ZoneInfo("America/Lima")))
        self.__user_repository.update(user)

        access_token = self.__jwt_service.create_access_token(user)
        refresh_token = self.__jwt_service.create_refresh_token(user)
        
        return {
            "user": user.to_external_dict(),
            "token": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }