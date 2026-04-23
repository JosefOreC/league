from .team import Team
from .user import User
from .institution import Institution
from .tournament_team_state import TournamentTeamState
from .tournament_rule import TournamentRule


class TournamentTeam:
    def __init__(
        self,
        id: str,
        tournament_id: int,
        tournament_rule: TournamentRule,
        state: TournamentTeamState,
        team: Team
    ):
        self.__id = id
        self.__team = team
        self.__tournament_id = tournament_id
        self.__state = state
        self.__tournament_rule = tournament_rule

        self.__validate_rules()

    @property
    def id(self) -> str:
        return self.__id

    @property
    def team(self) -> Team:
        return self.__team

    @property
    def members(self) -> tuple[User]:
        return self.__team.members

    @property
    def leader(self) -> User:
        return self.__team.leader

    @property
    def teacher(self) -> User:
        return self.__team.teacher

    @property
    def institution(self) -> Institution:
        return self.__team.institution

    @property
    def tournament_id(self) -> int:
        return self.__tournament_id

    @property
    def tournament_rule(self) -> TournamentRule:
        return self.__tournament_rule

    @property
    def state(self) -> TournamentTeamState:
        return self.__state

    @state.setter
    def state(self, state: TournamentTeamState):
        if not isinstance(state, TournamentTeamState):
            raise ValueError("El state debe ser un TournamentTeamState")
        self.__state = state

    def add_member(self, member: User):
        if len(self.__team.members) + 1 > self.__tournament_rule.max_members:
            raise ValueError("Se excede el máximo de miembros permitido por el torneo")

        self.__team.add_member(member)

    def remove_member(self, member: User):
        if len(self.__team.members) - 1 < self.__tournament_rule.min_members:
            raise ValueError("Se viola el mínimo de miembros permitido por el torneo")

        self.__team.remove_member(member)

        if self.__team.leader and self.__team.leader.id == member.id:
            self.__team.change_leader(None)

    def change_leader(self, leader: User):
        self.__team.change_leader(leader)

    def change_teacher(self, teacher: User):
        self.__team.change_teacher(teacher)

    def __validate_rules(self):
        size = len(self.__team.members)

        if size < self.__tournament_rule.min_members:
            raise ValueError("El equipo no cumple el mínimo de miembros del torneo")

        if size > self.__tournament_rule.max_members:
            raise ValueError("El equipo excede el máximo de miembros del torneo")