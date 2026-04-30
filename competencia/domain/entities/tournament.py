from competencia.domain.value_objects.config_tournament.config_knockout import ConfigKnockout
from .tournament_team import TournamentTeam
from datetime import datetime, timezone
from ..value_objects.enums.tournament_state import TournamentState
from .tournament_rule import TournamentRule
from .team import Team
from ..value_objects.enums.tournament_team_state import TournamentTeamState
from uuid import uuid4
from ..value_objects.enums.tournament_category import TournamentCategory
from ..value_objects.enums.tournament_rol import TournamentRol
from .tournament_member import TournamentMember
from ..value_objects.enums.tournament_type import TournamentType
from ..value_objects.config_tournament.config_tournament import ConfigTournament
from ..value_objects.config_tournament.config_tournament_factory import ConfigTournamentFactory
from ..value_objects.config_tournament.config_round_robin import ConfigRoundRobin
from ..value_objects.config_tournament.config_hybrid import ConfigHybrid
from ..value_objects.config_tournament.tournament_evaluation import TournamentEvaluation

class Tournament:

    def __init__(self, id: str, name:str, description:str, date_start:datetime, date_end:datetime,
                tournament_rule: TournamentRule, state:TournamentState, creator_user_id, 
                category: TournamentCategory, users_tournaments: list[TournamentMember],
                teams: list[TournamentTeam]=None, tournament_type: TournamentType = TournamentType.KNOCKOUT, 
                config_tournament:ConfigTournament=None, tournament_evaluation:TournamentEvaluation=None):
        self.__name = name
        self.__description = description
        if date_start > date_end:
            raise ValueError("La fecha de inicio debe ser menor a la fecha de fin")
        self.__date_start = date_start
        self.__date_end = date_end
        self.__creator_user_id = creator_user_id
        self.__tournament_teams = teams if teams is not None else []
        self.__tournament_rule = tournament_rule
        self.__tournament_type = tournament_type
        self.__state = state
        self.__category = category
        self.__id = id
        self.__config_tournament = config_tournament
        self.__tournament_evaluation = tournament_evaluation
        if not users_tournaments:
            raise ValueError("El torneo debe tener al menos un usuario")
        self.__users_tournaments = users_tournaments
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        date_start: datetime,
        date_end: datetime,
        max_teams: int,
        creator_user_id: str, category: TournamentCategory
    ):
        now = datetime.now()

        if date_start <= now:
            raise ValueError("La fecha de inicio debe ser posterior a hoy")

        if date_end <= date_start:
            raise ValueError("La fecha de fin debe ser posterior al inicio")
        id = str(uuid4())
        tournament_rule = TournamentRule.create(max_teams=max_teams)
        users_tournaments = [TournamentMember(user_id=creator_user_id, tournament_id=id, rol=TournamentRol.MANAGER)]
        config_tournament = ConfigKnockout.create()
        tournament_evaluation = TournamentEvaluation.create()

        return cls(
            id=id,
            name=name,
            description=description,
            date_start=date_start,
            date_end=date_end,
            tournament_rule=tournament_rule,
            state=TournamentState.DRAFT,
            creator_user_id=creator_user_id,
            category=category,
            teams=[],
            users_tournaments=users_tournaments,
            config_tournament=config_tournament,
            tournament_evaluation=tournament_evaluation
        )

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
    def creator_user_id(self) -> str:
        return self.__creator_user_id

    @property
    def tournament_rule(self) -> TournamentRule:
        return self.__tournament_rule

    @property
    def config_tournament(self) -> ConfigTournament:
        return self.__config_tournament

    @property
    def tournament_evaluation(self) -> TournamentEvaluation:
        return self.__tournament_evaluation

    @property
    def state(self) -> TournamentState:
        return self.__state

    @property
    def category(self) -> TournamentCategory:
        return self.__category

    @property
    def users_tournaments(self) -> tuple[TournamentMember]:
        return tuple(self.__users_tournaments)

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

    @creator_user_id.setter
    def creator_user_id(self, creator_user_id: str):
        if not isinstance(creator_user_id, str) or not creator_user_id:
            raise ValueError("El creador debe ser una cadena no vacía")
        self.__creator_user_id = creator_user_id

    # METODOS PRIMITIVOS
    
    def add_team(self, team: Team):
        if not isinstance(team, Team):
            raise ValueError("El equipo debe ser de tipo Team")
        
        if self.__state != TournamentState.REGISTRATION_OPEN:
            raise ValueError("El torneo no está abierto para inscripciones")

        if len(self.get_teams_accepted()) >= self.__tournament_rule.max_teams:
            raise ValueError("El torneo ha alcanzado el número máximo de equipos aprobados")
        
        # Validar reglas de equipo (miembros min/max, institución)
        self.__tournament_rule.validate_team_rules(team)

        # Validar participante duplicado por DNI en el mismo torneo
        for tt in self.__tournament_teams:
            for p_existing in tt.team.participants:
                for p_new in team.participants:
                    if p_existing.documento_identidad == p_new.documento_identidad:
                        raise ValueError(f"El participante con documento {p_new.documento_identidad} ya está inscrito en este torneo")

        tournament_team = TournamentTeam(
            id=str(uuid4()),
            tournament_id=self.id,
            state=TournamentTeamState.PENDING,
            member_in_tournament_func=self.member_in_tournament,
            team=team,
            qualify_score_team=[]
        )
        self.__tournament_teams.append(tournament_team)

    def remove_team(self, team_id: str):
        for tt in self.__tournament_teams:
            if tt.team.id == team_id:
                self.__tournament_teams.remove(tt)
                return
        raise ValueError("El equipo no está inscrito en el torneo")
    
    def get_rol_by_user(self, user_id: str) -> TournamentRol | None:
        """Devuelve el rol del usuario en el torneo, o None si no participa."""
        for m in self.__users_tournaments:
            if m.user_id == user_id:
                return m.rol
        return None

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
    def update_tournament_rules(self, tournament_rule: TournamentRule, tournament_config: ConfigTournament, tournament_evaluation: TournamentEvaluation):
        if self.__state != TournamentState.DRAFT:
            raise ValueError("El torneo no está en estado de borrador")
        self.__tournament_rule = TournamentRule(
            id=self.__tournament_rule.id,
            min_members=tournament_rule.min_members,
            max_members=tournament_rule.max_members,
            min_teams=tournament_rule.min_teams,
            max_teams=tournament_rule.max_teams,
            created_at=self.__tournament_rule.created_at,
            updated_at=datetime.now(),
            validation_list=list(tournament_rule.validation_list),
            access_type=tournament_rule.access_type
        )
        self.__config_tournament = tournament_config
        self.__tournament_evaluation = tournament_evaluation

    def update_state(self, new_state: TournamentState):
        if self.validate_state_transition(new_state):
            self.__state = new_state

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
                TournamentState.IN_REVIEW,
                TournamentState.REGISTRATION_CLOSED
            },
            TournamentState.REGISTRATION_CLOSED: {
                TournamentState.IN_PROGRESS
            },
            TournamentState.IN_PROGRESS: {
                TournamentState.FINALIZED,
                TournamentState.CANCELLED
            },
            TournamentState.CANCELLED: {
                TournamentState.DRAFT,
                TournamentState.IN_REVIEW,
                TournamentState.REGISTRATION_OPEN,
                TournamentState.REGISTRATION_CLOSED,
                TournamentState.IN_PROGRESS
            }
        }

        allowed = valid_transitions.get(self.__state, set())

        if new_state not in allowed:
            raise ValueError(
                f"Transición inválida: {self.__state} → {new_state}"
            )
        return True


    # METODOS DE VERIFICACION
    def contains_team(self, team_id: str) -> bool:
        for t in self.__tournament_teams:
            if t.team.id == team_id:
                return True
        return False
    
    def is_full(self) -> bool:
        return len(self.get_teams_accepted()) >= self.__tournament_rule.max_teams
    
    def to_dict(self) -> dict:
        return {
            "id":              self.id,
            "name":            self.__name,
            "description":     self.__description,
            "date_start":      self.__date_start.isoformat(),
            "date_end":        self.__date_end.isoformat(),
            "state":           self.__state.value,
            "category":        self.__category.value,
            "creator_user_id": self.__creator_user_id,
            "users_tournaments": [{"user_id": m.user_id, "tournament_id": m.tournament_id, "rol": m.rol.value} for m in self.__users_tournaments],
            "tournament_rule": self.__tournament_rule.to_dict(),
            "tournament_evaluation": self.__tournament_evaluation.to_dict() if self.__tournament_evaluation else None,
            "config_tournament": self.__config_tournament.to_dict() if self.__config_tournament else None,
            "teams": [t.to_dict() for t in self.__tournament_teams]
        }
    
    def valid_for_review(self) -> bool:
        rules_config = self.__get_tournament_args()
        self.__config_tournament.validate(**rules_config)
        self.__tournament_evaluation.valid_criterias()
        return True
    
    def update_tournament_evaluation(self, tournament_evaluation:TournamentEvaluation):
        if self.__state != TournamentState.DRAFT:
            raise ValueError("El torneo no está en estado de borrador")
        self.__tournament_evaluation = tournament_evaluation
    
    def rechazed_all_teams_not_accepted(self):
        for team in self.get_teams_pending():
            if team.state == TournamentTeamState.PENDING:
                team.state = TournamentTeamState.REFUSED

    def validate_for_start(self) -> bool:
        # HU-GT-04 Scenario 4: Validar equipos con participantes suficientes
        for tt in self.get_teams_accepted():
            self.__tournament_rule.validate_team_rules(tt.team)
            
        self.__tournament_rule.validate_tournament_teams(self.get_teams_accepted())
        self.__config_tournament.validate_for_start(**self.__get_tournament_args())
        return True
    
    def __get_tournament_args(self) -> dict:
        return {
            "tournament_teams_accepted_count": len(self.get_teams_accepted()),
            "max_teams": self.__tournament_rule.max_teams,
        }

    def member_in_tournament(self, member_identifier: str) -> bool:
        for t in self.__tournament_teams:
            for p in t.team.participants:
                if p.documento_identidad == member_identifier or p.id == member_identifier:
                    return True
        return False