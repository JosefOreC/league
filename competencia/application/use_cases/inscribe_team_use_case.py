from ...domain.ports.team_repository import TeamRepository
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.team import Team
from ...domain.entities.participant import Participant
from uuid import uuid4

class InscribeTeamUseCase:
    def __init__(self, team_repository: TeamRepository, tournament_repository: TournamentRepository):
        self.__team_repository = team_repository
        self.__tournament_repository = tournament_repository

    def execute(self, tournament_id: str, team_data: dict, participants_data: list[dict]):
        tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("Torneo no encontrado")

        participants = [Participant.from_dict(p) for p in participants_data]
        
        team = Team(
            id=str(uuid4()),
            tournament_id=tournament_id,
            name=team_data["name"],
            category=team_data["category"],
            institution_id=team_data["institution_id"],
            nivel_tecnico_declarado=team_data["nivel_tecnico_declarado"],
            representante_id=team_data["representante_id"],
            docente_asesor_id=team_data["docente_asesor_id"],
            participants=participants
        )

        # La validación ocurre dentro de add_team en el dominio (uniqueness, capacity, etc)
        tournament.add_team(team)
        
        # Persistir el equipo
        self.__team_repository.save(team)
        
        return team.to_dict()
