from abc import ABC, abstractmethod
from ..entities.team import Team

class TeamRepository(ABC):
    @abstractmethod
    def save(self, team: Team):
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> Team | None:
        pass
    
    @abstractmethod
    def find_all(self) -> list[Team]:
        pass
    
    @abstractmethod
    def delete(self, id: str):
        pass
    
    @abstractmethod
    def update(self, team: Team):
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> list[Team] | None:
        pass
    
    @abstractmethod
    def find_by_creator_user(self, creator_user_id: str) -> list[Team]:
        pass
    
    @abstractmethod
    def find_by_institution(self, institution_id: str) -> list[Team]:
        pass
    
    @abstractmethod
    def find_by_teacher(self, teacher_id: str) -> list[Team]:
        pass

    @abstractmethod
    def find_by_tournament(self, tournament_id: str) -> list[Team]:
        pass