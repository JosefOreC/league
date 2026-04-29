from .config_tournament import ConfigTournament
from ..enums.tournament_type import TournamentType

class ConfigHybrid(ConfigTournament):
    def __init__(
        self, teams_for_group: int, classified_by_group: int, num_rounds: int,
        third_place: bool,  final_format: TournamentType = TournamentType.KNOCKOUT
    ):
        if not isinstance(teams_for_group, int):
            raise ValueError("El número de equipos por grupo debe ser un entero")
        if not isinstance(classified_by_group, int):
            raise ValueError("El número de clasificados por grupo debe ser un entero")
        if not isinstance(num_rounds, int):
            raise ValueError("El número de rondas debe ser un entero")
        if not isinstance(third_place, bool):
            raise ValueError("El tercer lugar debe ser un booleano")
        if not isinstance(final_format, TournamentType):
            raise ValueError("El formato final debe ser un tipo de torneo")
        self.__teams_for_group = teams_for_group
        self.__classified_by_group = classified_by_group
        self.__num_rounds = num_rounds
        self.__final_format = final_format
        self.__third_place = third_place

    def validate(self, max_teams: int) -> bool:
        if self.__classified_by_group > self.__teams_for_group:
            raise ValueError("El número de clasificados por grupo debe ser menor o igual al número de equipos por grupo")
        if self.__num_rounds <= 0:
            raise ValueError("El número de rondas debe ser mayor a 0")
        if self.__teams_for_group <= 1:
            raise ValueError("El número de equipos por grupo debe ser mayor a 1")
        if max_teams < 6:
            raise ValueError("Se requiere un mínimo de 6 equipos para esta configuración")
    
    def to_dict(self) -> dict[str, any]:
        return {
            "teams_for_group": self.__teams_for_group,
            "classified_by_group": self.__classified_by_group,
            "num_rounds": self.__num_rounds,
            "final_format": self.__final_format,
            "third_place": self.__third_place
        }

    @property
    def teams_for_group(self) -> int:
        return self.__teams_for_group

    @property
    def classified_by_group(self) -> int:
        return self.__classified_by_group

    @property
    def num_rounds(self) -> int:
        return self.__num_rounds

    @property
    def final_format(self) -> TournamentType:
        return self.__final_format

    @property
    def third_place(self) -> bool:
        return self.__third_place