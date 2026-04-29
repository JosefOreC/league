from ...domain.entities.tournament import Tournament
from ...domain.entities.tournament_rule import TournamentRule
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.user import User
from authentication.domain.value_objects.enum.user_state import UserState
from ...domain.value_objects.enums.tournament_rol import TournamentRol

class ConfigTournamentRuleUseCase:
    def __init__(self, tournament_repository: TournamentRepository, user:User):
        self.__tournament_repository = tournament_repository
        self.__user = user

    def execute(self, tournament_rule: TournamentRule, tournament_id: str):
        tournament: Tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("El torneo no existe")
        self._validate_user(tournament.get_rol_by_user(self.__user.id))
        tournament.update_tournament_rules(tournament_rule)
        self.__tournament_repository.update(tournament=tournament)
        return tournament

    def _validate_user(self, user_tournament_role: TournamentRol):
        if self.__user.state != UserState.ACTIVE:
            raise ValueError("Usuario inactivo")
        if user_tournament_role != TournamentRol.MANAGER:
            raise ValueError("El usuario no es el manager del torneo")
        
        