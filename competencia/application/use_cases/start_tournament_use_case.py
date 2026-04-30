from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.user import User
from ...domain.entities.tournament import Tournament
from ...domain.value_objects.enums.tournament_state import TournamentState
from ...domain.value_objects.enums.tournament_rol import TournamentRol

class StartTournamentUseCase:
    def __init__(self, tournament_repository: TournamentRepository, user: User):
        self.__tournament_repository = tournament_repository
        self.__user = user
    
    def execute(self, tournament_id: str) -> None:
        tournament:Tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("El torneo no existe.")
        self.__valid_permissions(tournament)
        tournament.validate_for_start()
        tournament.update_state(TournamentState.IN_PROGRESS)
        self.__tournament_repository.update(tournament)
    
    def __valid_permissions(self, tournament: Tournament) -> bool:
        if not tournament.validate_state_transition(TournamentState.IN_PROGRESS):
            raise ValueError("El torneo está en un estado que no permite iniciar.")
        if not tournament.get_rol_by_user(self.__user.id) == TournamentRol.MANAGER:
            raise PermissionError("El usuario no tiene permisos para iniciar el torneo.")
        return True