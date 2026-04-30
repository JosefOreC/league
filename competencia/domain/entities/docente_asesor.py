from uuid import uuid4

class DocenteAsesor:
    def __init__(self, id: str, nombre_completo: str, email: str, telefono: str, institution_id: str):
        self.__id = id
        self.__nombre_completo = nombre_completo
        self.__email = email
        self.__telefono = telefono
        self.__institution_id = institution_id

    @property
    def id(self) -> str: return self.__id
    @property
    def nombre_completo(self) -> str: return self.__nombre_completo
    @property
    def email(self) -> str: return self.__email
    @property
    def telefono(self) -> str: return self.__telefono
    @property
    def institution_id(self) -> str: return self.__institution_id

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "nombre_completo": self.__nombre_completo,
            "email": self.__email,
            "telefono": self.__telefono,
            "institution_id": self.__institution_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DocenteAsesor':
        return cls(
            id=data.get("id", str(uuid4())),
            nombre_completo=data["nombre_completo"],
            email=data["email"],
            telefono=data["telefono"],
            institution_id=data["institution_id"]
        )
