from uuid import uuid4
from datetime import datetime, timezone

class MatchResult:
    def __init__(self, id: str, match_id: str, equipo_id: str, criterio_id: str,
                 valor_registrado: float, valor_normalizado: float,
                 estado_resultado: str, registrado_por: str,
                 created_at: datetime = None, updated_at: datetime = None):
        self.__id = id
        self.__match_id = match_id
        self.__equipo_id = equipo_id
        self.__criterio_id = criterio_id
        self.__valor_registrado = valor_registrado
        self.__valor_normalizado = valor_normalizado
        self.__estado_resultado = estado_resultado # PARTIAL | DEFINITIVE
        self.__registrado_por = registrado_por
        self.__created_at = created_at or datetime.now()
        self.__updated_at = updated_at or datetime.now()

    @property
    def id(self) -> str: return self.__id
    @property
    def match_id(self) -> str: return self.__match_id
    @property
    def equipo_id(self) -> str: return self.__equipo_id
    @property
    def criterio_id(self) -> str: return self.__criterio_id
    @property
    def valor_registrado(self) -> float: return self.__valor_registrado
    @property
    def valor_normalizado(self) -> float: return self.__valor_normalizado
    @property
    def estado_resultado(self) -> str: return self.__estado_resultado
    @property
    def registrado_por(self) -> str: return self.__registrado_por
    @property
    def created_at(self) -> datetime: return self.__created_at
    @property
    def updated_at(self) -> datetime: return self.__updated_at

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "match_id": self.__match_id,
            "equipo_id": self.__equipo_id,
            "criterio_id": self.__criterio_id,
            "valor_registrado": self.__valor_registrado,
            "valor_normalizado": self.__valor_normalizado,
            "estado_resultado": self.__estado_resultado,
            "registrado_por": self.__registrado_por,
            "created_at": self.__created_at.isoformat() if isinstance(self.__created_at, datetime) else self.__created_at,
            "updated_at": self.__updated_at.isoformat() if isinstance(self.__updated_at, datetime) else self.__updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MatchResult':
        return cls(
            id=data.get("id", str(uuid4())),
            match_id=data["match_id"],
            equipo_id=data["equipo_id"],
            criterio_id=data["criterio_id"],
            valor_registrado=data["valor_registrado"],
            valor_normalizado=data["valor_normalizado"],
            estado_resultado=data["estado_resultado"],
            registrado_por=data["registrado_por"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
