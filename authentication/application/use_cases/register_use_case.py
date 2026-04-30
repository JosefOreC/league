from ...domain.entities.user import User
from ...domain.value_objects.enum.system_rol import SystemRol
from ...domain.value_objects.enum.user_state import UserState
from ...domain.ports.user_repository import UserRepository
from datetime import datetime
from ..service.password_service import PasswordService

class RegisterUseCase:
    """
    Caso de uso para gestionar el registro de nuevos usuarios en el sistema.
    """
    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        self.__user_repository = user_repository
        self.__password_service = password_service

    def execute(self, email: str, password: str, name: str, birth_date: datetime, rol: str = "participant"):
        # Validación de existencia previa de la cuenta
        existing_user = self.__user_repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"Cuenta con el correo {email} ya existe.")
        
        # Mapeo de rol desde string a objeto de dominio SystemRol
        try:
            system_rol = SystemRol(rol)
        except ValueError:
            system_rol = SystemRol.PARTICIPANT

        User.verify_password_security(password)
        password_hash = self.__password_service.encrypt_password(password=password)
        
        # Persistencia del usuario con el rol especificado
        new_user = User.create_user(email=email, rol=system_rol, password_hash=password_hash, name=name, birth_date=birth_date)
        self.__user_repository.create(new_user)