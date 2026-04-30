from abc import ABC, abstractmethod
from ..entities.participant import Participant

class ParticipantRepository(ABC):
    @abstractmethod
    def save(self, participant: Participant):
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> Participant | None:
        pass
    
    @abstractmethod
    def find_by_team(self, team_id: str) -> list[Participant]:
        pass
    
    @abstractmethod
    def find_by_document(self, document_id: str) -> Participant | None:
        pass

    @abstractmethod
    def delete(self, id: str):
        pass
