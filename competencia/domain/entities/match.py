from uuid import uuid4
from datetime import datetime

class Match:
    def __init__(self, id: str, tournament_id: str, ronda: int, posicion_en_ronda: int,
                 equipo_local_id: str = None, equipo_visitante_id: str = None,
                 es_bye: bool = False, es_descanso: bool = False,
                 grupo_id: str = None, fase: str = None,
                 estado: str = "PENDING", ganador_id: str = None,
                 partido_siguiente_id: str = None, fecha_programada: datetime = None):
        self.__id = id
        self.__tournament_id = tournament_id
        self.__ronda = ronda
        self.__posicion_en_ronda = posicion_en_ronda
        self.__equipo_local_id = equipo_local_id
        self.__equipo_visitante_id = equipo_visitante_id
        self.__es_bye = es_bye
        self.__es_descanso = es_descanso
        self.__grupo_id = grupo_id
        self.__fase = fase
        self.__estado = estado
        self.__ganador_id = ganador_id
        self.__partido_siguiente_id = partido_siguiente_id
        self.__fecha_programada = fecha_programada

    @property
    def id(self) -> str: return self.__id
    @property
    def tournament_id(self) -> str: return self.__tournament_id
    @property
    def ronda(self) -> int: return self.__ronda
    @property
    def posicion_en_ronda(self) -> int: return self.__posicion_en_ronda
    @property
    def equipo_local_id(self) -> str: return self.__equipo_local_id
    @property
    def equipo_visitante_id(self) -> str: return self.__equipo_visitante_id
    @property
    def es_bye(self) -> bool: return self.__es_bye
    @property
    def es_descanso(self) -> bool: return self.__es_descanso
    @property
    def grupo_id(self) -> str: return self.__grupo_id
    @property
    def fase(self) -> str: return self.__fase
    @property
    def estado(self) -> str: return self.__estado
    @property
    def ganador_id(self) -> str: return self.__ganador_id
    @property
    def partido_siguiente_id(self) -> str: return self.__partido_siguiente_id
    @property
    def fecha_programada(self) -> datetime: return self.__fecha_programada

    def set_teams(self, local_id: str, visitor_id: str):
        self.__equipo_local_id = local_id
        self.__equipo_visitante_id = visitor_id

    def set_winner(self, winner_id: str):
        self.__ganador_id = winner_id
        self.__estado = "FINISHED"

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "tournament_id": self.__tournament_id,
            "ronda": self.__ronda,
            "posicion_en_ronda": self.__posicion_en_ronda,
            "equipo_local_id": self.__equipo_local_id,
            "equipo_visitante_id": self.__equipo_visitante_id,
            "es_bye": self.__es_bye,
            "es_descanso": self.__es_descanso,
            "grupo_id": self.__grupo_id,
            "fase": self.__fase,
            "estado": self.__estado,
            "ganador_id": self.__ganador_id,
            "partido_siguiente_id": self.__partido_siguiente_id,
            "fecha_programada": self.__fecha_programada.isoformat() if self.__fecha_programada else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Match':
        return cls(
            id=data.get("id", str(uuid4())),
            tournament_id=data["tournament_id"],
            ronda=data["ronda"],
            posicion_en_ronda=data["posicion_en_ronda"],
            equipo_local_id=data.get("equipo_local_id"),
            equipo_visitante_id=data.get("equipo_visitante_id"),
            es_bye=data.get("es_bye", False),
            es_descanso=data.get("es_descanso", False),
            grupo_id=data.get("grupo_id"),
            fase=data.get("fase"),
            estado=data.get("estado", "PENDING"),
            ganador_id=data.get("ganador_id"),
            partido_siguiente_id=data.get("partido_siguiente_id"),
            fecha_programada=data.get("fecha_programada")
        )
