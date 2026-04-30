from abc import ABC, abstractmethod
from ..entities.standing import Standing

class StandingRepository(ABC):
    @abstractmethod
    def save(self, standing: Standing):
        pass
    
    @abstractmethod
    def find_by_tournament(self, tournament_id: str) -> list[Standing]:
        pass
    
    @abstractmethod
    def find_by_group(self, group_id: str) -> list[Standing]:
        pass
    
    @abstractmethod
    def delete_by_tournament(self, tournament_id: str):
        pass
