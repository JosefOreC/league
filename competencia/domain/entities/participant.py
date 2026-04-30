from datetime import date
from uuid import uuid4

class Participant:
    def __init__(self, id: str, nombres: str, apellidos: str, 
                 documento_identidad: str, email: str = None, 
                 birth_date: date = None, autorizacion_datos: bool = True):
        self.__id = id
        self.__nombres = nombres
        self.__apellidos = apellidos
        self.__documento_identidad = documento_identidad
        self.__email = email
        self.__birth_date = birth_date
        self.__autorizacion_datos = autorizacion_datos
        
        if not autorizacion_datos:
            raise ValueError("El consentimiento de tratamiento de datos es obligatorio")

    @property
    def id(self) -> str: return self.__id
    @property
    def nombres(self) -> str: return self.__nombres
    @property
    def apellidos(self) -> str: return self.__apellidos
    @property
    def documento_identidad(self) -> str: return self.__documento_identidad
    @property
    def email(self) -> str: return self.__email
    @property
    def birth_date(self) -> date: return self.__birth_date

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "nombres": self.__nombres,
            "apellidos": self.__apellidos,
            "documento_identidad": self.__documento_identidad,
            "email": self.__email,
            "birth_date": self.__birth_date.isoformat() if self.__birth_date else None,
            "autorizacion_datos": self.__autorizacion_datos
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Participant':
        return cls(
            id=data.get("id", str(uuid4())),
            nombres=data["nombres"],
            apellidos=data["apellidos"],
            documento_identidad=data["documento_identidad"],
            email=data.get("email"),
            birth_date=date.fromisoformat(data["birth_date"]) if data.get("birth_date") else None,
            autorizacion_datos=data.get("autorizacion_datos", True)
        )