from abc import ABC, abstractmethod
from ..entities.match import Match

class MatchRepository(ABC):
    @abstractmethod
    def save(self, match: Match):
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> Match | None:
        pass
    
    @abstractmethod
    def find_by_tournament(self, tournament_id: str) -> list[Match]:
        pass
    
    @abstractmethod
    def find_by_group(self, group_id: str) -> list[Match]:
        pass

    @abstractmethod
    def delete_by_tournament(self, tournament_id: str):
        pass
