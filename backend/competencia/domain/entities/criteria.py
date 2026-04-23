import uuid
from datetime import datetime, timezone

class Criteria:
    def __init__(self, id:str, name:str, description:str, created_at:datetime, updated_at:datetime, value: float):
        self.__id = id
        self.__name = name.upper()
        self.__description = description
        self.__created_at = created_at
        self.__updated_at = updated_at
        if value > 1.0 or value < 0.0:
            raise ValueError("El valor debe estar entre 0.0 y 1.0")
        self.__value = value
    
    @classmethod
    def create(cls, name:str, description:str, value:float):
        return cls(id=str(uuid.uuid4()), name=name, description=description, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), value=value)

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
    
    def touch(self):
        self.__updated_at = datetime.now(timezone.utc)

    def update_criteria(self, name:str, description:str, value:float):
        self.__name = name
        self.__description = description
        if value > 1.0 or value < 0.0:
            raise ValueError("El valor debe estar entre 0.0 y 1.0")
        self.__value = value
        self.touch()
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Criteria):
            return False
        return self.id == o.id
    
    def __hash__(self) -> int:
        return hash(self.id)