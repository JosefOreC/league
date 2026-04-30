class Standing:
    def __init__(self, tournament_id: str, team_id: str, group_id: str = None,
                 partidos_jugados: int = 0, victorias: int = 0, empates: int = 0,
                 derrotas: int = 0, puntos: int = 0, puntaje_favor: float = 0,
                 puntaje_contra: float = 0, diferencia_puntaje: float = 0,
                 posicion: int = 0):
        self.__tournament_id = tournament_id
        self.__team_id = team_id
        self.__group_id = group_id
        self.__partidos_jugados = partidos_jugados
        self.__victorias = victorias
        self.__empates = empates
        self.__derrotas = derrotas
        self.__puntos = puntos
        self.__puntaje_favor = puntaje_favor
        self.__puntaje_contra = puntaje_contra
        self.__diferencia_puntaje = diferencia_puntaje
        self.__posicion = posicion

    @property
    def tournament_id(self) -> str: return self.__tournament_id
    @property
    def team_id(self) -> str: return self.__team_id
    @property
    def group_id(self) -> str: return self.__group_id
    @property
    def partidos_jugados(self) -> int: return self.__partidos_jugados
    @property
    def victorias(self) -> int: return self.__victorias
    @property
    def empates(self) -> int: return self.__empates
    @property
    def derrotas(self) -> int: return self.__derrotas
    @property
    def puntos(self) -> int: return self.__puntos
    @property
    def puntaje_favor(self) -> float: return self.__puntaje_favor
    @property
    def puntaje_contra(self) -> float: return self.__puntaje_contra
    @property
    def diferencia_puntaje(self) -> float: return self.__diferencia_puntaje
    @property
    def posicion(self) -> int: return self.__posicion

    def update(self, win: bool = False, draw: bool = False, loss: bool = False, 
               points_for: float = 0, points_against: float = 0, pts: int = 0):
        self.__partidos_jugados += 1
        if win: self.__victorias += 1
        if draw: self.__empates += 1
        if loss: self.__derrotas += 1
        self.__puntos += pts
        self.__puntaje_favor += points_for
        self.__puntaje_contra += points_against
        self.__diferencia_puntaje = self.__puntaje_favor - self.__puntaje_contra

    def to_dict(self) -> dict:
        return {
            "tournament_id": self.__tournament_id,
            "team_id": self.__team_id,
            "group_id": self.__group_id,
            "partidos_jugados": self.__partidos_jugados,
            "victorias": self.__victorias,
            "empates": self.__empates,
            "derrotas": self.__derrotas,
            "puntos": self.__puntos,
            "puntaje_favor": float(self.__puntaje_favor),
            "puntaje_contra": float(self.__puntaje_contra),
            "diferencia_puntaje": float(self.__diferencia_puntaje),
            "posicion": self.__posicion
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Standing':
        return cls(
            tournament_id=data["tournament_id"],
            team_id=data["team_id"],
            group_id=data.get("group_id"),
            partidos_jugados=data.get("partidos_jugados", 0),
            victorias=data.get("victorias", 0),
            empates=data.get("empates", 0),
            derrotas=data.get("derrotas", 0),
            puntos=data.get("puntos", 0),
            puntaje_favor=data.get("puntaje_favor", 0),
            puntaje_contra=data.get("puntaje_contra", 0),
            diferencia_puntaje=data.get("diferencia_puntaje", 0),
            posicion=data.get("posicion", 0)
        )
