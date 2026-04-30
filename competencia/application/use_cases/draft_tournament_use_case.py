from ...domain.value_objects.enums.tournament_state import TournamentState
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.tournament import Tournament
from ...domain.entities.user import User
from ...domain.value_objects.enums.tournament_rol import TournamentRol


class DraftTournamentUseCase:
    def __init__(self, tournament_repository: TournamentRepository, user: User):
        self.tournament_repository = tournament_repository
        self.__user = user

    def execute(self, tournament_id: str):
        tournament = self.tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("El torneo no existe")
        self._validate_permissions(tournament)
        tournament.update_state(TournamentState.DRAFT)
        self.tournament_repository.update(tournament)
        return tournament
    
    def _validate_permissions(self, tournament: Tournament):
        if not (tournament.get_rol_by_user(self.__user.id) == TournamentRol.MANAGER):
            raise PermissionError("No tienes permisos para realizar esta acción")
        if not tournament.validate_state_transition(TournamentState.DRAFT):
            raise ValueError("El torneo no se puede pasar a borrador")
