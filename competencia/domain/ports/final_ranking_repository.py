from abc import ABC, abstractmethod
from ..entities.final_ranking import FinalRanking

class FinalRankingRepository(ABC):
    @abstractmethod
    def save(self, ranking: FinalRanking):
        pass
    
    @abstractmethod
    def find_by_tournament(self, tournament_id: str) -> list[FinalRanking]:
        pass
    
    @abstractmethod
    def delete_by_tournament(self, tournament_id: str):
        pass
