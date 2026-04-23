# PENDIENTE DE DISERTACION
from abc import ABC, abstractmethod
from ..entities.tournament_rule import TournamentRule


class TournamentRuleRepository(ABC):
    @abstractmethod
    def save(self, tournament_rule: TournamentRule) -> None:
        pass

    @abstractmethod
    def find_by_id(self, id: str) -> TournamentRule | None:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

    @abstractmethod
    def update(self, tournament_rule: TournamentRule) -> None:
        pass

    @abstractmethod
    def find_all(self) -> list[TournamentRule]:
        pass

    @abstractmethod
    def recover_by_tournament_id(self, tournament_id: str) -> TournamentRule:
        pass