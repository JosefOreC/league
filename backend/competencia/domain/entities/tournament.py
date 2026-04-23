from .tournament_team import TournamentTeam
from .user import User
from datetime import datetime
from ..value_objects.enums.tournament_state import TournamentState
from ..value_objects.tournament_rule import TournamentRule
from .team import Team
from ..value_objects.enums.tournament_team_state import TournamentTeamState


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

    # METODOS PRIMITIVOS

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
    
    # METODOS DE RECUPERACIÓN DE EQUIPOS
    def search_team_by_id(self, team_id:str) -> TournamentTeam | None:
        for t in self.__tournament_teams:
            if t.team.id == team_id:
                return t
        raise ValueError("El equipo no está inscrito en el torneo")

    def get_teams(self) -> tuple[TournamentTeam]:
        return tuple(self.__tournament_teams)
    
    def get_teams_pending(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.PENDING]

    def get_teams_accepted(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.ACCEPTED]

    def get_teams_disqualified(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.DISQUALIFIED]

    def get_teams_retirated(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.RETIRATED]
    
    # METODOS DE ACTUALIZACIÓN
    def update_tournament_rules(self, tournament_rule: TournamentRule):
        if self.__state != TournamentState.DRAFT:
            raise ValueError("El torneo no está en estado de borrador")
        self.__tournament_rule = tournament_rule

    def update_state(self, new_state: TournamentState):
        if self.validate_state_transition(new_state):
            self.__state = new_state

    # METODOS ESPECIFICOS DE FASE DE INSCRIPCION
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

    # METODOS DE VALIDACION DE FLUJO DE ESTADO
    def validate_state_transition(self, new_state: TournamentState)->bool:
        valid_transitions = {
            TournamentState.DRAFT: {
                TournamentState.IN_REVIEW
            },
            TournamentState.IN_REVIEW: {
                TournamentState.DRAFT,
                TournamentState.REGISTRATION_OPEN
            },
            TournamentState.REGISTRATION_OPEN: {
                TournamentState.REGISTRATION_CLOSED
            },
            TournamentState.REGISTRATION_CLOSED: {
                TournamentState.IN_PROGRESS
            },
            TournamentState.IN_PROGRESS: {
                TournamentState.FINALIZED,
                TournamentState.CANCELLED
            }
        }

        allowed = valid_transitions.get(self.__state, set())

        if new_state not in allowed:
            raise ValueError(
                f"Transición inválida: {self.__state} → {new_state}"
            )
        return True


    # METODOS DE VERIFICACION
    def contains_team(self, team: Team) -> bool:
        for t in self.__tournament_teams:
            if t.team.id == team.id:
                return True
        return False
    
    def is_full(self) -> bool:
        return len(self.__tournament_teams) == self.__tournament_rule.max_teams



    

   
    
    

    