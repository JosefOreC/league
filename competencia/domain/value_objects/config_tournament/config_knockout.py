from .config_tournament import ConfigTournament
from ...entities.tournament import Tournament

class ConfigKnockout(ConfigTournament):
    def __init__(self, seed_enabled:bool, third_place:bool, best_of:int):
        if not isinstance(self.__seed_enabled, bool):
            raise ValueError("El seed_enabled debe ser un booleano")
        if not isinstance(self.__third_place, bool):
            raise ValueError("El third_place debe ser un booleano")
        if not isinstance(self.__best_of, int) or not self.__best_of:
            raise ValueError("El best_of debe ser un entero no vacío")
        self.__seed_enabled = seed_enabled
        self.__third_place = third_place
        self.__best_of = best_of
    
    @property
    def third_place(self) -> bool:
        return self.__third_place
    
    @property
    def best_of(self) -> int:
        return self.__best_of
    
    def validate(self, tournament_teams_count: int) -> bool:
        if tournament_teams_count < 2:
            raise ValueError("El número de equipos debe ser mayor o igual a 2")
        if tournament_teams_count % 2 != 0:
            raise ValueError("El número de equipos debe ser par")
        if self.__best_of <= 0:
            raise ValueError("El best_of debe ser mayor a 0")
        return True
    
    def to_dict(self):
        return {
            "seed_enabled": self.__seed_enabled,
            "third_place": self.__third_place,
            "best_of": self.__best_of,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    def __eq__(self, other):
        if not isinstance(other, ConfigKnockout):
            return False
        return self.to_dict() == other.to_dict()
    
    @property
    def seed_enabled(self) -> bool:
        return self.__seed_enabled
    