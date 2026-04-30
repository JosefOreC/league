from ...domain.entities.tournament import Tournament
from ...domain.entities.tournament_rule import TournamentRule
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.user import User
from authentication.domain.value_objects.enum.user_state import UserState
from ...domain.value_objects.enums.tournament_rol import TournamentRol
from ...domain.value_objects.config_tournament.config_tournament_factory import ConfigTournamentFactory
from ...domain.value_objects.config_tournament.tournament_evaluation import TournamentEvaluation

class ConfigTournamentRuleUseCase:
    def __init__(self, tournament_repository: TournamentRepository, user:User):
        self.__tournament_repository = tournament_repository
        self.__user = user

    def execute(self, tournament_rule: dict, tournament_id: str, tournament_config:dict, tournament_evaluation:dict):
        tournament: Tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("El torneo no existe")
        self._validate_user(tournament.get_rol_by_user(self.__user.id))
        tournament_config_obj = ConfigTournamentFactory.create_config_tournament(tournament_config["type"], tournament_config["config"])
        tournament_rule_obj = TournamentRule.from_dict(**tournament_rule)
        tournament_evaluation_obj = TournamentEvaluation.from_dict(**tournament_evaluation)
        tournament.update_tournament_rules(tournament_rule=tournament_rule_obj, tournament_config=tournament_config_obj, tournament_evaluation=tournament_evaluation_obj)
        self.__tournament_repository.update(tournament=tournament)
        return tournament

    def _validate_user(self, user_tournament_role: TournamentRol):
        if self.__user.state != UserState.ACTIVE:
            raise ValueError("Usuario inactivo")
        if user_tournament_role != TournamentRol.MANAGER:
            raise ValueError("El usuario no es el manager del torneo")
        
        