from ..entities.user import User
import uuid
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        raise NotImplementedError
    
    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> User:
        raise NotImplementedError
    
    @abstractmethod
    def get_by_email(self, email: str) -> User:
        raise NotImplementedError
    
    @abstractmethod
    def update(self, user: User) -> User:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, id: uuid.UUID) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def recover(self, email: str) -> dict:
        raise NotImplementedError