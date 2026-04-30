from ...domain.ports.team_repository import TeamRepository

class GetTeamsByTournamentUseCase:
    def __init__(self, team_repository: TeamRepository):
        self.__team_repository = team_repository

    def execute(self, tournament_id: str):
        return self.__team_repository.find_by_tournament(tournament_id)
