from ...domain.ports.team_repository import TeamRepository

class RejectTeamUseCase:
    def __init__(self, team_repository: TeamRepository):
        self.__team_repository = team_repository

    def execute(self, team_id: str):
        team = self.__team_repository.find_by_id(team_id)
        if not team:
            raise ValueError("Equipo no encontrado")
        
        team.reject()
        self.__team_repository.update(team)
        return team
