from datetime import date
from uuid import uuid4

class Participant:
    def __init__(self, id: str, nombres: str, apellidos: str, 
                 documento_identidad: str, edad: int = 0, grado_academico: str = "",
                 rol_en_equipo: str = "", email: str = None, 
                 birth_date: date = None, autorizacion_datos: bool = True):
        self.__id = id
        self.__nombres = nombres
        self.__apellidos = apellidos
        self.__documento_identidad = documento_identidad
        self.__edad = edad
        self.__grado_academico = grado_academico
        self.__rol_en_equipo = rol_en_equipo
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
    def edad(self) -> int: return self.__edad
    @property
    def grado_academico(self) -> str: return self.__grado_academico
    @property
    def rol_en_equipo(self) -> str: return self.__rol_en_equipo
    @property
    def email(self) -> str: return self.__email
    @property
    def birth_date(self) -> date: return self.__birth_date
    @property
    def autorizacion_datos(self) -> bool: return self.__autorizacion_datos

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "nombres": self.__nombres,
            "apellidos": self.__apellidos,
            "documento_identidad": self.__documento_identidad,
            "edad": self.__edad,
            "grado_academico": self.__grado_academico,
            "rol_en_equipo": self.__rol_en_equipo,
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
            edad=data.get("edad", 0),
            grado_academico=data.get("grado_academico", ""),
            rol_en_equipo=data.get("rol_en_equipo", ""),
            email=data.get("email"),
            birth_date=date.fromisoformat(data["birth_date"]) if data.get("birth_date") else None,
            autorizacion_datos=data.get("autorizacion_datos", True)
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Participant):
            return False
        return self.documento_identidad == other.documento_identidad

    def __hash__(self) -> int:
        return hash(self.documento_identidad)

    def __str__(self) -> str:
        return f"{self.nombres} {self.apellidos}"