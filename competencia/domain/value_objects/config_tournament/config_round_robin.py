from .config_tournament import ConfigTournament

class ConfigRoundRobin(ConfigTournament):
    NAME = "round_robin"
    def __init__(self, num_rounds: int, point_to_victory: int, point_to_draw: int, 
                point_to_defeat: int, tie_breaking_criteria: list[str]):
        if not isinstance(num_rounds, int):
            raise ValueError("El número de rondas debe ser un entero")
        if not isinstance(point_to_victory, int):
            raise ValueError("El número de puntos a la victoria debe ser un entero")
        if not isinstance(point_to_draw, int):
            raise ValueError("El número de puntos al empate debe ser un entero")
        if not isinstance(point_to_defeat, int):
            raise ValueError("El número de puntos a la derrota debe ser un entero")
        if not isinstance(tie_breaking_criteria, list):
            raise ValueError("Los criterios de desempate deben ser una lista")
        self.__num_rounds = num_rounds
        self.__point_to_victory = point_to_victory
        self.__point_to_draw = point_to_draw
        self.__point_to_defeat = point_to_defeat
        self.__tie_breaking_criteria = tie_breaking_criteria
    
    def validate(self) -> bool:
        if self.__tie_breaking_criteria is None or len(self.__tie_breaking_criteria) == 0:
            raise ValueError("Debe existir al menos un criterio de desempate")
        if self.__point_to_victory <= self.__point_to_draw or self.__point_to_draw <= self.__point_to_defeat:
            raise ValueError("Los puntos deben ser ordenados de mayor a menor")
        return True
    
    def to_dict(self):
        return {
            "type": self.NAME,
            "config":{
                "num_rounds": self.__num_rounds,
                "point_to_victory": self.__point_to_victory,
                "point_to_draw": self.__point_to_draw,
                "point_to_defeat": self.__point_to_defeat,
                "tie_breaking_criteria": self.__tie_breaking_criteria,
            }
        }

    @property
    def num_rounds(self) -> int:
        return self.__num_rounds

    @property
    def point_to_victory(self) -> int:
        return self.__point_to_victory

    @property
    def point_to_draw(self) -> int:
        return self.__point_to_draw

    @property
    def point_to_defeat(self) -> int:
        return self.__point_to_defeat

    @property
    def tie_breaking_criteria(self) -> list[str]:
        return self.__tie_breaking_criteria
    
    def validate_for_start(self, tournament_teams_accepted_count:int, **args) -> bool:
        if tournament_teams_accepted_count != (2 ** self.__best_of):
            raise ValueError("El número de equipos debe ser par")
        return True