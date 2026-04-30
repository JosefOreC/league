from ...domain.entities.user import User
from ...domain.value_objects.enum.system_rol import SystemRol
from ...domain.value_objects.enum.user_state import UserState
from ...domain.ports.user_repository import UserRepository
from datetime import datetime
from ..service.password_service import PasswordService

class RegisterUseCase:
    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        self.__user_repository = user_repository
        self.__password_service = password_service

    def execute(self, email: str, password: str, name: str, birth_date: datetime):
        existing_user = self.__user_repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"Cuenta con el correo {email} ya existe.")
        User.verify_password_security(password)
        password_hash = self.__password_service.encrypt_password(password=password)
        new_user = User.create_user(email=email, rol=SystemRol.PARTICIPANT, password_hash=password_hash, name=name, birth_date=birth_date)
        self.__user_repository.create(new_user)
    