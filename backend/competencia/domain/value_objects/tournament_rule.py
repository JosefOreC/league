from datetime import datetime
from ..entities.team import Team
from ..entities.tournament_team import TournamentTeam
from ..entities.institution import Institution
from .enums.tournament_access_type import TournamentAccessType

class TournamentRule:
    def __init__(self, id:str, tournament_id:str, min_members:int, max_members:int, min_teams:int, max_teams:int, created_at:datetime, updated_at:datetime, 
                validation_list: list[Institution] = None, access_type:TournamentAccessType = TournamentAccessType.PRIVATE,):
        self.__id = id
        self.__tournament_id = tournament_id
        self.__min_members = min_members
        self.__max_members = max_members
        self.__min_teams = min_teams
        self.__max_teams = max_teams
        self.__created_at = created_at
        self.__updated_at = updated_at
        self.__validation_list = validation_list if validation_list is not None else []
        self.__access_type = access_type
        

    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def tournament_id(self) -> str:
        return self.__tournament_id
    
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
    
    @min_members.setter
    def min_members(self, min_members: int):
        if not isinstance(min_members, int) or min_members < 1:
            raise ValueError("El número mínimo de miembros debe ser mayor o igual a 1")
        self.__min_members = min_members

    @max_members.setter
    def max_members(self, max_members: int):
        if not isinstance(max_members, int) or max_members < 1:
            raise ValueError("El número máximo de miembros debe ser mayor o igual a 1")
        self.__max_members = max_members
    
    @min_teams.setter
    def min_teams(self, min_teams: int):
        if not isinstance(min_teams, int) or min_teams < 1:
            raise ValueError("El número mínimo de equipos debe ser mayor o igual a 1")
        self.__min_teams = min_teams
    
    @max_teams.setter
    def max_teams(self, max_teams: int):
        if not isinstance(max_teams, int) or max_teams < 1:
            raise ValueError("El número máximo de equipos debe ser mayor o igual a 1")
        self.__max_teams = max_teams
    
    def validate_team_rules(self, team: Team):
        if len(team.members) < self.__min_members:
            raise ValueError("El equipo no cumple el mínimo de miembros del torneo")
        if len(team.members) > self.__max_members:
            raise ValueError("El equipo excede el máximo de miembros del torneo")
        if self.__access_type == TournamentAccessType.PUBLIC:
            return True
        if team.institution not in self.__validation_list:
            raise ValueError("El equipo no pertenece a ninguna institución participante")
        return True
    
    def validate_tournament_teams(self, tournament_teams: list[TournamentTeam]):
        if len(tournament_teams) < self.__min_teams:
            raise ValueError("El torneo no cumple el mínimo de equipos inscritos")
        if len(tournament_teams) > self.__max_teams:
            raise ValueError("El torneo excede el máximo de equipos inscritos")
        return True
    
    def tournament_can_start(self, tournament_teams: list[TournamentTeam]) -> bool:
        for tournament_team in tournament_teams:
            self.validate_team_rules(tournament_team.team)
        return self.validate_tournament_teams(tournament_teams)