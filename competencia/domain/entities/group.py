from uuid import uuid4

class Group:
    def __init__(self, id: str, tournament_id: str, name: str):
        self.__id = id
        self.__tournament_id = tournament_id
        self.__name = name

    @property
    def id(self) -> str: return self.__id
    @property
    def tournament_id(self) -> str: return self.__tournament_id
    @property
    def name(self) -> str: return self.__name

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "tournament_id": self.__tournament_id,
            "name": self.__name
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Group':
        return cls(
            id=data.get("id", str(uuid4())),
            tournament_id=data["tournament_id"],
            name=data["name"]
        )
