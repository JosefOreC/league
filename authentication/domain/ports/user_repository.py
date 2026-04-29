from ..entities.user import User
import uuid

class UserRepository:
    def create(self, user: User) -> User:
        raise NotImplementedError
    
    def get_by_id(self, id: uuid.UUID) -> User:
        raise NotImplementedError
    
    def get_by_email(self, email: str) -> User:
        raise NotImplementedError
    
    def update(self, user: User) -> User:
        raise NotImplementedError
    
    def delete(self, id: uuid.UUID) -> None:
        raise NotImplementedError
    
    def recover(self, email: str) -> dict:
        raise NotImplementedError