from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.tournament import Tournament
from ...domain.entities.user import User
from authentication.domain.value_objects.enum.system_rol import SystemRol
from ...domain.value_objects.enums.tournament_rol import TournamentRol
from ...domain.value_objects.enums.tournament_state import TournamentState

class CancellTournamentUseCase:
    def __init__(self, tournament_repository: TournamentRepository, user: User):
        self.__tournament_repository = tournament_repository
        self.__user = user
    
    def execute(self, tournament_id: str) -> Tournament:
        tournament:Tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("El torneo no existe.")
        self.__valid_permissions(tournament)
        tournament.update_state(TournamentState.CANCELLED)
        self.__tournament_repository.update(tournament)
        return tournament
    
    def __valid_permissions(self, tournament: Tournament) -> bool:
        if not tournament.validate_state_transition(TournamentState.CANCELLED):
            raise ValueError("El torneo está en un estado que no permite ser cancelado.")
        if not tournament.get_rol_by_user(self.__user.id) == TournamentRol.MANAGER:
            raise PermissionError("El usuario no tiene permisos para cancelar el torneo.")
        if self.__user.rol == SystemRol.ADMIN:
            return True
        return True