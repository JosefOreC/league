from ...domain.entities.user import User
from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState

class UserCompentenciaService:
    def dict_to_user(data)->User:
        user = User(
            id=data.get("user_id", "1"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            rol=SystemRol(data.get("rol", "admin")),
            state=UserState(data.get("state", "active")),
        )
        return user

        

        