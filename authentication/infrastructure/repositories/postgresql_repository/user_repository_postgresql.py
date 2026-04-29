import uuid
from django.core.exceptions import ObjectDoesNotExist
from authentication.domain.ports.user_repository import UserRepository
from authentication.domain.entities.user import User
from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState
from authentication.infrastructure.adapters.output.models import UserModel

class UserRepositoryPostgresql(UserRepository):
    
    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=uuid.UUID(model.id) if model.id else None,
            email=model.email,
            password_hash=model.password_hash,
            name=model.name,
            rol=SystemRol(model.rol),
            state=UserState(model.state),
            birth_date=model.birth_date,
            attempts=model.attempts,
            blocked_until=model.blocked_until,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            id=str(user.id),
            email=user.email,
            password_hash=user.password_hash,
            name=user.name,
            rol=user.rol.value,
            state=user.state.value,
            birth_date=user.birth_date,
            attempts=user.attempts,
            blocked_until=user.blocked_until,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )

    def create(self, user: User) -> User:
        model = self._to_model(user)
        model.save()
        return user
    
    def get_by_id(self, id: uuid.UUID) -> User:
        try:
            model = UserModel.objects.get(id=str(id))
            return self._to_domain(model)
        except ObjectDoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> User:
        try:
            model = UserModel.objects.get(email=email)
            return self._to_domain(model)
        except ObjectDoesNotExist:
            return None
    
    def update(self, user: User) -> User:
        model = self._to_model(user)
        model.save()
        return user
    
    def delete(self, id: uuid.UUID) -> None:
        UserModel.objects.filter(id=str(id)).delete()

    def recover(self, email: str) -> dict:
        user = self.get_by_email(email)
        if user:
            return user.to_internal_dict()
        return None
