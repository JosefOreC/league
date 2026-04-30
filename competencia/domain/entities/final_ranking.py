class FinalRanking:
    def __init__(self, tournament_id: str, team_id: str, posicion_final: int,
                 puntaje_total_acumulado: float, medalla: str = None,
                 mencion_especial: str = None):
        self.__tournament_id = tournament_id
        self.__team_id = team_id
        self.__posicion_final = posicion_final
        self.__puntaje_total_acumulado = puntaje_total_acumulado
        self.__medalla = medalla
        self.__mencion_especial = mencion_especial

    @property
    def tournament_id(self) -> str: return self.__tournament_id
    @property
    def team_id(self) -> str: return self.__team_id
    @property
    def posicion_final(self) -> int: return self.__posicion_final
    @property
    def puntaje_total_acumulado(self) -> float: return self.__puntaje_total_acumulado
    @property
    def medalla(self) -> str: return self.__medalla
    @property
    def mencion_especial(self) -> str: return self.__mencion_especial

    def to_dict(self) -> dict:
        return {
            "tournament_id": self.__tournament_id,
            "team_id": self.__team_id,
            "posicion_final": self.__posicion_final,
            "puntaje_total_acumulado": float(self.__puntaje_total_acumulado),
            "medalla": self.__medalla,
            "mencion_especial": self.__mencion_especial
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FinalRanking':
        return cls(
            tournament_id=data["tournament_id"],
            team_id=data["team_id"],
            posicion_final=data["posicion_final"],
            puntaje_total_acumulado=data["puntaje_total_acumulado"],
            medalla=data.get("medalla"),
            mencion_especial=data.get("mencion_especial")
        )
