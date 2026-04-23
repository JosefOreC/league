from abc import ABC, abstractmethod
from ..entities.tournament import Tournament
from ..entities.tournament_rule import TournamentRule

class TournamentRepository(ABC):
    @abstractmethod
    def save(self, tournament: Tournament):
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> Tournament | None:
        pass
    
    @abstractmethod
    def find_all(self) -> list[Tournament]:
        pass
    
    @abstractmethod
    def find_by_team_id(self, team_id: int) -> list[Tournament]:
        pass
    
    @abstractmethod
    def delete(self, id: int):
        pass
    
    @abstractmethod
    def update(self, tournament: Tournament):
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> list[Tournament] | None:
        pass
    
    @abstractmethod
    def recover_tournament_rules(self, tournament_id: int) -> TournamentRule | None:
        pass
    
    

