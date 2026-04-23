from abc import ABC, abstractmethod
from ..entities.tournament_team import TournamentTeam

class TournamentTeamRepository(ABC):
    @abstractmethod
    def save(self, tournament_team: TournamentTeam):
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> TournamentTeam | None:
        pass
    
    @abstractmethod
    def find_all(self) -> list[TournamentTeam]:
        pass
    
    @abstractmethod
    def delete(self, id: str):
        pass
    
    @abstractmethod
    def update(self, tournament_team: TournamentTeam):
        pass
    
    @abstractmethod
    def find_by_tournament(self, tournament_id: str) -> list[TournamentTeam]:
        pass
    
    @abstractmethod
    def find_by_team(self, team_id: str) -> list[TournamentTeam]:
        pass
    
    @abstractmethod
    def find_by_state(self, state: str) -> list[TournamentTeam]:
        pass
    