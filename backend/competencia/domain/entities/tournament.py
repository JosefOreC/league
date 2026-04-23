from .tournament_team import TournamentTeam
from .user import User
from datetime import datetime
from .tournament_state import TournamentState
from .tournament_rule import TournamentRule
from .team import Team
from .tournament_team_state import TournamentTeamState


class Tournament:
    def __init__(self, id: str, name:str, description:str, date_start:datetime, date_end:datetime,
                tournament_rule: TournamentRule, state:TournamentState, 
                creator_user:User=None, teams: list[TournamentTeam]=None):
        self.__name = name
        self.__description = description
        self.__date_start = date_start
        self.__date_end = date_end
        self.__creator_user = creator_user
        self.__tournament_teams = teams if teams is not None else []
        self.__tournament_rule = tournament_rule
        self.__state = state
        self.__id = id
    
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
    def date_start(self) -> datetime:
        return self.__date_start
    
    @property
    def date_end(self) -> datetime:
        return self.__date_end
    
    @property
    def creator_user(self) -> User:
        return self.__creator_user
    
    @name.setter
    def name(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError("El nombre debe ser una cadena no vacía")
        self.__name = name
    
    @description.setter
    def description(self, description: str):
        if not isinstance(description, str) or not description:
            raise ValueError("La descripción debe ser una cadena no vacía")
        self.__description = description
    
    @date_start.setter
    def date_start(self, date_start: datetime):
        if not isinstance(date_start, datetime):
            raise ValueError("La fecha debe ser una fecha")
        self.__date_start = date_start
    
    @date_end.setter
    def date_end(self, date_end: datetime):
        if not isinstance(date_end, datetime):
            raise ValueError("La fecha debe ser una fecha")
        if date_end < self.__date_start:
            raise ValueError("La fecha de fin debe ser mayor a la fecha de inicio")
        self.__date_end = date_end

    @creator_user.setter
    def creator_user(self, creator_user: User):
        if not isinstance(creator_user, User):
            raise ValueError("El creador debe ser un usuario")
        self.__creator_user = creator_user

    def __add_team(self, team: TournamentTeam):
        if not isinstance(team, TournamentTeam):
            raise ValueError("El equipo debe ser un equipo de torneo (TournamentTeam)")
        if len(self.__tournament_teams) >= self.__tournament_rule.max_teams:
            raise ValueError("El torneo ha alcanzado el número máximo de equipos")
        self.__tournament_teams.append(team)

    def __remove_team(self, team: Team):
        if not isinstance(team, Team):
            raise ValueError("El equipo debe ser de tipo Team")
        if not self.contains_team(team):
            raise ValueError("El equipo no está inscrito en el torneo")
        for t in self.__tournament_teams:
            if t.team.id == team.id:
                self.__tournament_teams.remove(t)
                break

    def get_teams(self) -> tuple[TournamentTeam]:
        return tuple(self.__tournament_teams)
    
    def register_team(self, team: Team):
        if self.__state != TournamentState.REGISTRATION_OPEN:
            raise ValueError("El torneo no está en estado de inscripción")
        if self.contains_team(team):
            raise ValueError("El equipo ya está inscrito en el torneo")
        self.__tournament_rule.validate_team_rules(team)
        new_tournament_team = TournamentTeam(id=team.id, team=team, tournament_id=self.id, tournament_rule=self.__tournament_rule, state=TournamentTeamState.PENDING)
        self.__add_team(new_tournament_team)

    def unregister_team(self, team: Team):
        if self.__state != TournamentState.REGISTRATION_OPEN:
            raise ValueError("El torneo no está en estado de inscripción")
        if not self.contains_team(team):
            raise ValueError("El equipo no está inscrito en el torneo")
        self.__remove_team(team)

    def contains_team(self, team: Team) -> bool:
        for t in self.__tournament_teams:
            if t.team.id == team.id:
                return True
        return False

    def search_team_by_id(self, team_id:str) -> TournamentTeam | None:
        for t in self.__tournament_teams:
            if t.team.id == team_id:
                return t
        raise ValueError("El equipo no está inscrito en el torneo")

    def get_teams_pending(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.PENDING]

    def get_teams_accepted(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.ACCEPTED]

    def get_teams_disqualified(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.DISQUALIFIED]

    def get_teams_retirated(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.RETIRATED]

    def is_full(self) -> bool:
        return len(self.__tournament_teams) == self.__tournament_rule.max_teams
    
    def update_tournament_rules(self, tournament_rule: TournamentRule):
        if self.__state != TournamentState.DRAFT:
            raise ValueError("El torneo no está en estado de borrador")
        self.__tournament_rule = tournament_rule

    def send_to_review(self):
        if self.__state != TournamentState.DRAFT:
            raise ValueError("El torneo no está en estado de borrador")
        self.__state = TournamentState.IN_REVIEW

    def back_to_draft(self):
        if self.__state != TournamentState.IN_REVIEW:
            raise ValueError("El torneo no está en estado de revisión")
        self.__state = TournamentState.DRAFT
    
    def open_inscription(self):
        if self.__state != TournamentState.IN_REVIEW:
            raise ValueError("El torneo no está en estado de revisión")
        self.__tournament_rule.validate_tournament_teams(self.get_teams())
        self.__state = TournamentState.REGISTRATION_OPEN
    
    def close_inscription(self):
        if self.__state != TournamentState.REGISTRATION_OPEN:
            raise ValueError("El torneo no está en estado de inscripción")
        self.__state = TournamentState.REGISTRATION_CLOSED
        
    def start_tournament(self):
        if self.__state != TournamentState.REGISTRATION_CLOSED:
            raise ValueError("El torneo no está en estado de inscripción cerrada")
        self.__state = TournamentState.IN_PROGRESS
    
    def end_tournament(self):
        if self.__state != TournamentState.IN_PROGRESS:
            raise ValueError("El torneo no está en estado de progreso")
        self.__state = TournamentState.FINALIZED
    
    def cancel_tournament(self):
        if self.__state != TournamentState.IN_PROGRESS:
            raise ValueError("El torneo no está en estado de progreso")
        self.__state = TournamentState.CANCELLED

        