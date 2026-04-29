from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.tournament import Tournament
from ...domain.entities.user import User
from ...domain.value_objects.enums.tournament_rol import TournamentRol
from ...domain.value_objects.enums.tournament_state import TournamentState

class ReviewTournamentUseCase:
    def __init__(self, tournament_repository: TournamentRepository, user:User):
        self.__tournament_repository = tournament_repository
        self.__user = user
    
    def execute(self, tournament_id: str) -> Tournament:
        tournament:Tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("El torneo no existe.")
        self.__valid_permissions(tournament)
        tournament.update_state(TournamentState.IN_REVIEW)
        self.__tournament_repository.update(tournament)
        return tournament

    def __valid_permissions(self, tournament: Tournament) -> bool:
        user_tournament = tournament.get_rol_by_user(self.__user.id)
        if user_tournament is None or user_tournament.rol != TournamentRol.MANAGER:
            raise PermissionError("El usuario no tiene permisos para realizar esta acción")
        if not tournament.validate_state_transition(TournamentState.IN_REVIEW):
            raise ValueError("El torneo está en un estado que no permite ser revisado.")
        if tournament.state == TournamentState.REGISTRATION_OPEN and tournament.get_teams():
            raise ValueError("El torneo tiene equipos registrados, no puede retroceder de estado.")
        if not tournament.validate_all_rules():
            raise ValueError("El torneo tiene configuraciones que no cumplen con las reglas.")
        return True

        