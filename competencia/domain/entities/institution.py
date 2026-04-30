from uuid import uuid4

class Institution:
    def __init__(self, id: str, name: str, type: str, city: str, country: str):
        self.__id = id
        self.__name = name
        self.__type = type
        self.__city = city
        self.__country = country

    @property
    def id(self) -> str: return self.__id
    @property
    def name(self) -> str: return self.__name
    @property
    def type(self) -> str: return self.__type
    @property
    def city(self) -> str: return self.__city
    @property
    def country(self) -> str: return self.__country

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "name": self.__name,
            "type": self.__type,
            "city": self.__city,
            "country": self.__country
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Institution':
        return cls(
            id=data.get("id", str(uuid4())),
            name=data["name"],
            type=data["type"],
            city=data["city"],
            country=data["country"]
        )