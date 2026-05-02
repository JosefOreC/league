from uuid import uuid4
from datetime import datetime, timezone
from .participant import Participant

class Team:
    def __init__(self, id: str, tournament_id: str, name: str, category: str, 
                 institution_id: str, nivel_tecnico_declarado: str, 
                 representante_id: str, docente_asesor_id: str, 
                 estado_inscripcion: str = "PENDIENTE", 
                 fecha_inscripcion: datetime = None,
                 participants: list[Participant] = None):
        self.__id = id
        self.__tournament_id = tournament_id
        self.__name = name
        self.__category = category # PRIMARY | SECONDARY
        self.__institution_id = institution_id
        self.__nivel_tecnico_declarado = nivel_tecnico_declarado
        self.__estado_inscripcion = estado_inscripcion
        self.__fecha_inscripcion = fecha_inscripcion or datetime.now()
        self.__representante_id = representante_id
        self.__docente_asesor_id = docente_asesor_id
        self.__participants = participants or []

    @property
    def id(self) -> str: return self.__id
    @property
    def tournament_id(self) -> str: return self.__tournament_id
    @property
    def name(self) -> str: return self.__name
    @property
    def category(self) -> str: return self.__category
    @property
    def institution_id(self) -> str: return self.__institution_id
    @property
    def nivel_tecnico_declarado(self) -> str: return self.__nivel_tecnico_declarado
    @property
    def estado_inscripcion(self) -> str: return self.__estado_inscripcion
    @property
    def fecha_inscripcion(self) -> datetime: return self.__fecha_inscripcion
    @property
    def representante_id(self) -> str: return self.__representante_id
    @property
    def docente_asesor_id(self) -> str: return self.__docente_asesor_id
    @property
    def participants(self) -> tuple[Participant]: return tuple(self.__participants)

    def add_participant(self, participant: Participant):
        self.__participants.append(participant)

    def approve(self):
        self.__estado_inscripcion = "APROBADO"

    def reject(self):
        self.__estado_inscripcion = "RECHAZADO"

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "tournament_id": self.__tournament_id,
            "name": self.__name,
            "category": self.__category,
            "institution_id": self.__institution_id,
            "nivel_tecnico_declarado": self.__nivel_tecnico_declarado,
            "estado_inscripcion": self.__estado_inscripcion,
            "fecha_inscripcion": self.__fecha_inscripcion.isoformat() if isinstance(self.__fecha_inscripcion, datetime) else self.__fecha_inscripcion,
            "representante_id": self.__representante_id,
            "docente_asesor_id": self.__docente_asesor_id,
            "participants": [p.to_dict() for p in self.__participants]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Team':
        participants_data = data.get("participants", [])
        return cls(
            id=data.get("id", str(uuid4())),
            tournament_id=data["tournament_id"],
            name=data["name"],
            category=data["category"],
            institution_id=data["institution_id"],
            nivel_tecnico_declarado=data["nivel_tecnico_declarado"],
            estado_inscripcion=data.get("estado_inscripcion", "PENDIENTE"),
            fecha_inscripcion=data.get("fecha_inscripcion"),
            representante_id=data["representante_id"],
            docente_asesor_id=data["docente_asesor_id"],
            participants=[Participant.from_dict(p) for p in participants_data]
        )
