from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.tournament import Tournament
from ...domain.entities.user import User
from ...domain.value_objects.enums.tournament_state import TournamentState
from ...domain.value_objects.enums.tournament_rol import TournamentRol

class CloseRegistrationsUseCase:
    def __init__(self, tournament_repository: TournamentRepository, user: User):
        self.__tournament_repository = tournament_repository
        self.__user = user
    
    def execute(self, tournament_id: str) -> Tournament:
        tournament:Tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("El torneo no existe.")
        if not self.__valid_permissions(tournament):
            raise PermissionError("El usuario no tiene permisos para cerrar inscripciones.")
        tournament.update_state(TournamentState.REGISTRATION_CLOSED)
        self.__tournament_repository.update(tournament)
        return tournament
    
    def __valid_permissions(self, tournament: Tournament) -> bool:
        if not tournament.validate_state_transition(TournamentState.REGISTRATION_CLOSED):
            raise ValueError("El torneo está en un estado que no permite cerrar inscripciones.")
        if not tournament.get_rol_by_user(self.__user.id) == TournamentRol.MANAGER:
            raise PermissionError("El usuario no tiene permisos para cerrar inscripciones.")
        return True