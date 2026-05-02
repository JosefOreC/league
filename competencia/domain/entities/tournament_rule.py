from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from .team import Team
from ..value_objects.enums.tournament_access_type import TournamentAccessType
from uuid import uuid4

if TYPE_CHECKING:
    from .tournament_team import TournamentTeam


class TournamentRule:
    def __init__(self, id:str, min_members:int, max_members:int, min_teams:int, max_teams:int, created_at:datetime, updated_at:datetime, 
                validation_list: list[str] = None, access_type:TournamentAccessType = TournamentAccessType.PRIVATE,
                date_start_inscription:datetime=None, date_end_inscription:datetime=None):
        self.__id = id
        if min_members > max_members:
            raise ValueError("El número mínimo de miembros debe ser menor o igual al número máximo de miembros")
        if max_members < 2:
            raise ValueError("El número máximo de miembros debe ser mayor o igual a 2")
        self.__min_members = min_members
        self.__max_members = max_members
        if min_teams > max_teams:
            raise ValueError("El número mínimo de equipos debe ser menor o igual al número máximo de equipos")
        if max_teams < 4:
            raise ValueError("El número máximo de equipos debe ser mayor o igual a 4")
        if max_teams > 64:
            raise ValueError("El número máximo de equipos debe ser menor o igual a 64")
        self.__min_teams = min_teams
        self.__max_teams = max_teams
        self.__created_at = created_at
        self.__updated_at = updated_at
        self.__validation_list = validation_list if validation_list is not None else []
        self.__access_type = access_type
        self.__date_start_inscription = date_start_inscription
        self.__date_end_inscription = date_end_inscription

    
    @classmethod
    def create(cls, max_teams:int, min_members:int=2, max_members:int=5, min_teams:int=4, validation_list: list[str] = None, access_type:TournamentAccessType = TournamentAccessType.PRIVATE, date_start_inscription:datetime=None, date_end_inscription:datetime=None):
        return cls(id=str(uuid4()), min_members=min_members, max_members=max_members, min_teams=min_teams, max_teams=max_teams, created_at=datetime.now(), updated_at=datetime.now(), validation_list=validation_list, access_type=access_type, date_start_inscription=date_start_inscription, date_end_inscription=date_end_inscription)

    @property
    def id(self) -> str:
        return self.__id
        
    @property
    def min_members(self) -> int:
        return self.__min_members
    
    @property
    def max_members(self) -> int:
        return self.__max_members
    
    @property
    def min_teams(self) -> int:
        return self.__min_teams
    
    @property
    def max_teams(self) -> int:
        return self.__max_teams
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    @property
    def updated_at(self) -> datetime:
        return self.__updated_at

    @property
    def access_type(self) -> TournamentAccessType:
        return self.__access_type

    @property
    def validation_list(self) -> tuple[str]:
        return tuple(self.__validation_list)

    @property
    def date_start_inscription(self) -> datetime | None:
        return self.__date_start_inscription

    @property
    def date_end_inscription(self) -> datetime | None:
        return self.__date_end_inscription

    @classmethod
    def from_dict(cls, **data) -> 'TournamentRule':
        start = data.get("date_start_inscription")
        if isinstance(start, str):
            try:
                start = datetime.fromisoformat(start)
                if start.tzinfo is not None:
                    start = start.replace(tzinfo=None)
            except ValueError:
                pass

        end = data.get("date_end_inscription")
        if isinstance(end, str):
            try:
                end = datetime.fromisoformat(end)
                if end.tzinfo is not None:
                    end = end.replace(tzinfo=None)
            except ValueError:
                pass

        return cls(
            id=data.get("id", str(uuid4())),
            min_members=data["min_members"],
            max_members=data["max_members"],
            min_teams=data["min_teams"],
            max_teams=data["max_teams"],
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at", datetime.now()),
            validation_list=data.get("validation_list", []),
            access_type=TournamentAccessType(data["access_type"]),
            date_start_inscription=start,
            date_end_inscription=end,
        )

    def touch(self):
        self.__updated_at = datetime.now()
    
    def validate_team_rules(self, team: Team) -> bool:
        if len(team.participants) < self.__min_members:
            raise ValueError(f"El equipo {team.name} requiere mínimo {self.__min_members} participantes")
        if len(team.participants) > self.__max_members:
            raise ValueError(f"El equipo {team.name} excede el máximo de {self.__max_members} participantes")
        if self.__access_type == TournamentAccessType.PUBLIC:
            return True
        if team.institution_id not in self.__validation_list:
            raise ValueError("La institución del equipo no está habilitada para este torneo")
        return True
    
    def validate_tournament_teams(self, tournament_teams: list[TournamentTeam]) -> bool:
        if len(tournament_teams) < self.__min_teams:
            raise ValueError("El torneo no cumple el mínimo de equipos inscritos")
        if len(tournament_teams) > self.__max_teams:
            raise ValueError("El torneo excede el máximo de equipos inscritos")
        return True
    
    def validate(self):
        if self.__max_members < self.__min_members:
            raise ValueError("El número máximo de miembros debe ser mayor o igual al número mínimo de miembros")
        if self.__max_teams < self.__min_teams:
            raise ValueError("El número máximo de equipos debe ser mayor o igual al número mínimo de equipos")
        if self.__date_start_inscription is None or self.__date_end_inscription is None:
            raise ValueError("Debe definir las fechas de inicio y fin de inscripción")
        if self.__date_start_inscription > self.__date_end_inscription:
            raise ValueError("La fecha de inicio de inscripción debe ser menor a la fecha de fin de inscripción")
        if self.__date_end_inscription < datetime.now():
            raise ValueError("La fecha de fin de inscripción debe ser mayor a la fecha actual")
        


    def to_dict(self):
        return {
            "id": self.id,
            "min_members": self.min_members,
            "max_members": self.max_members,
            "min_teams": self.min_teams,
            "max_teams": self.max_teams,
            "access_type": self.access_type.value,
            "validation_list": list(self.validation_list),
            "date_start_inscription": self.__date_start_inscription.isoformat() if self.__date_start_inscription else None,
            "date_end_inscription": self.__date_end_inscription.isoformat() if self.__date_end_inscription else None,
        }