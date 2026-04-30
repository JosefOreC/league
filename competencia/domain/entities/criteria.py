from __future__ import annotations
import uuid
from datetime import datetime, timezone

class Criteria:
    def __init__(self, id:str, name:str, description:str, min_value_qualification:float, max_value_qualification:float, created_at:datetime, updated_at:datetime, value: float):
        self.__id = id
        self.__name = name.upper()
        self.__description = description
        if min_value_qualification > max_value_qualification:
            raise ValueError("El valor mínimo debe ser menor o igual al valor máximo")
        self.__min_value_qualification = min_value_qualification
        self.__max_value_qualification = max_value_qualification
        self.__created_at = created_at
        self.__updated_at = updated_at
        if value > 1.0 or value < 0.0:
            raise ValueError("El valor debe estar entre 0.0 y 1.0")
        self.__value = value
    
    @classmethod
    def create(cls, name:str, description:str, min_value:float, max_value:float, value:float):
        return cls(id=str(uuid.uuid4()), name=name, description=description, min_value=min_value, max_value=max_value, created_at=datetime.now(), updated_at=datetime.now(), value=value)

    @property
    def id(self) -> str:
        return self.__id
        
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def description(self) -> str:
        return self.__description
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    @property
    def updated_at(self) -> datetime:
        return self.__updated_at

    @property
    def value(self) -> float:
        return self.__value
    
    def touch(self):
        self.__updated_at = datetime.now()

    def update_criteria(self, name:str, description:str, value:float):
        self.__name = name
        self.__description = description
        if value > 1.0 or value < 0.0:
            raise ValueError("El valor debe estar entre 0.0 y 1.0")
        self.__value = value
        self.touch()

    def to_dict(self) -> dict[str, any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "min_value": self.__min_value_qualification,
            "max_value": self.__max_value_qualification,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, **data) -> Criteria:
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            description=data.get("description", ""),
            min_value_qualification=data["min_value"],
            max_value_qualification=data["max_value"],
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at", datetime.now()),
            value=data["value"]
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Criteria):
            return False
        return self.id == o.id
    
    def __hash__(self) -> int:
        return hash(self.id)