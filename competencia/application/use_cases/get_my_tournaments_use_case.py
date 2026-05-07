from ...domain.ports.team_repository import TeamRepository
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.user import User

class GetMyTournamentsUseCase:
    """
    Devuelve todos los torneos en los que el usuario autenticado
    tiene un equipo inscrito (como representante).
    """

    def __init__(self, team_repository: TeamRepository, tournament_repository: TournamentRepository):
        self.__team_repository = team_repository
        self.__tournament_repository = tournament_repository

    def execute(self, user: User) -> list[dict]:
        # 1. Obtener los equipos donde el usuario esta presente
        teams = self.__team_repository.find_by_creator_user(user.id)
        if not teams:
            return []
            
        # 2. Obtener los torneos usando el nuevo método del repositorio
        tournaments = self.__tournament_repository.find_my_tournaments(user.id)
        tournament_map = {t.id: t for t in tournaments}

        # 3. Combinar ambos para el frontend
        result = []
        seen_tournament_ids = set()

        for team in teams:
            tournament_id = team.tournament_id
            if tournament_id in seen_tournament_ids:
                continue
            seen_tournament_ids.add(tournament_id)

            tournament = tournament_map.get(tournament_id)
            if tournament:
                result.append({
                    "tournament": tournament.to_dict(),
                    "team": team.to_dict()
                })

        return result
