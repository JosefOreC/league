from abc import ABC, abstractmethod
from ..entities.match_result import MatchResult

class MatchResultRepository(ABC):
    @abstractmethod
    def save(self, result: MatchResult):
        pass
    
    @abstractmethod
    def find_by_match(self, match_id: str) -> list[MatchResult]:
        pass
    
    @abstractmethod
    def find_by_team_in_match(self, team_id: str, match_id: str) -> list[MatchResult]:
        pass
