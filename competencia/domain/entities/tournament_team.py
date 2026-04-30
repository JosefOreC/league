from .team import Team
from .participant import Participant
from ..value_objects.enums.tournament_team_state import TournamentTeamState
from .qualify_score_team import QualifyScoreTeam

class TournamentTeam:
    def __init__(
        self,
        id: str,
        tournament_id: str,
        state: TournamentTeamState,
        member_in_tournament_func: callable,
        team: Team,
        qualify_score_team: list[QualifyScoreTeam]
    ):
        self.__id = id
        self.__team = team
        self.__tournament_id = tournament_id
        self.__state = state
        self.__member_in_tournament_func = member_in_tournament_func
        self.__qualify_score_team = qualify_score_team or []
        self.__validate_rules()

    def __validate_rules(self):
        if not self.__id:
            raise ValueError("TournamentTeam requiere un ID")
        if not self.__team:
            raise ValueError("TournamentTeam requiere un equipo asociado")
        if not isinstance(self.__state, TournamentTeamState):
            raise ValueError("TournamentTeam requiere un estado válido")

    @property
    def id(self) -> str:
        return self.__id

    @property
    def team(self) -> Team:
        return self.__team

    @property
    def participants(self) -> tuple[Participant]:
        return self.__team.participants

    @property
    def institution_id(self) -> str:
        return self.__team.institution_id

    @property
    def tournament_id(self) -> str:
        return self.__tournament_id

    @property
    def state(self) -> TournamentTeamState:
        return self.__state

    @state.setter
    def state(self, state: TournamentTeamState):
        if not isinstance(state, TournamentTeamState):
            raise ValueError("El state debe ser un TournamentTeamState")
        self.__state = state

    def add_participant(self, participant: Participant):
        if len(self.__team.participants) + 1 > self.__tournament_rule.max_members:
            raise ValueError("Se excede el máximo de miembros permitido por el torneo")
        self.__team.add_participant(participant)

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "tournament_id": self.__tournament_id,
            "state": self.__state.value,
            "team": self.__team.to_dict(),
            "qualify_score_team": [q.to_dict() for q in self.__qualify_score_team] if self.__qualify_score_team else []
        }
