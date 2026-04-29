from ...domain.entities.tournament import Tournament
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.user import User
from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState
from datetime import datetime
from ...domain.value_objects.enums.tournament_category import TournamentCategory

class CreateTournamentUseCase:
    def __init__(self, user: User, tournament_repository: TournamentRepository):
        self.__tournament_repository = tournament_repository
        self.__user = user

    def execute(self, name: str, description: str, date_start: datetime, date_end: datetime, category: TournamentCategory, max_teams: int):
        self._validate_user()
        tournament = Tournament.create(name=name, description=description, date_start=date_start, date_end=date_end, max_teams=max_teams, creator_user_id=self.__user.id, category=category)
        self.__tournament_repository.save(tournament=tournament)
        return tournament

    def _validate_user(self):
        if self.__user.rol not in [SystemRol.ADMIN, SystemRol.MANAGER]:
            raise ValueError("Sin permisos")
        if self.__user.state != UserState.ACTIVE:
            raise ValueError("Usuario inactivo")