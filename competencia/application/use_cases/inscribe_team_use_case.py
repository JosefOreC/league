from ...domain.ports.team_repository import TeamRepository
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.ports.institution_repository import InstitutionRepository
from ...domain.ports.docente_asesor_repository import DocenteAsesorRepository
from ...domain.entities.team import Team
from ...domain.entities.participant import Participant
from ...domain.entities.institution import Institution
from ...domain.entities.docente_asesor import DocenteAsesor
from ...domain.entities.user import User
from uuid import uuid4

class InscribeTeamUseCase:
    def __init__(
        self, 
        team_repository: TeamRepository, 
        tournament_repository: TournamentRepository,
        institution_repository: InstitutionRepository,
        docente_repository: DocenteAsesorRepository
    ):
        self.__team_repository = team_repository
        self.__tournament_repository = tournament_repository
        self.__institution_repository = institution_repository
        self.__docente_repository = docente_repository

    def execute(self, tournament_id: str, team_data: dict, participants_data: list[dict], user: User):
        tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("Torneo no encontrado")

        institution_id = team_data.get("institution_id")
        if not institution_id and "institution" in team_data:
            inst_data = team_data["institution"]
            institution = Institution.from_dict(inst_data)
            self.__institution_repository.save(institution)
            institution_id = institution.id
        
        if not institution_id:
            raise ValueError("Se requiere una institución válida para el equipo")

        docente_id = team_data.get("docente_asesor_id")
        if not docente_id and "docente_asesor" in team_data:
            doc_data = team_data["docente_asesor"]
            doc_data["institution_id"] = institution_id
            
            existing_doc = self.__docente_repository.find_by_email(doc_data["email"])
            if existing_doc:
                docente_id = existing_doc.id
            else:
                docente = DocenteAsesor.from_dict(doc_data)
                self.__docente_repository.save(docente)
                docente_id = docente.id

        if not docente_id:
            raise ValueError("Se requiere un docente asesor para el equipo")

        participants = [Participant.from_dict(p) for p in participants_data]
        
        team = Team(
            id=str(uuid4()),
            tournament_id=tournament_id,
            name=team_data.get("name", team_data.get("nombre")),
            category=team_data.get("category", team_data.get("categoria")),
            institution_id=institution_id,
            nivel_tecnico_declarado=team_data.get("nivel_tecnico_declarado"),
            representante_id=user.id,
            docente_asesor_id=docente_id,
            participants=participants
        )

        tournament.add_team(team)
        self.__team_repository.save(team)        
        return team.to_dict()
