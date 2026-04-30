from ....domain.ports.team_repository import TeamRepository
from ....domain.entities.team import Team
from ....domain.entities.participant import Participant
from ...adapters.output.models import TeamModel, ParticipantModel
from uuid import uuid4
from datetime import datetime

class TeamRepositoryPostgresql(TeamRepository):

    @staticmethod
    def _participant_to_domain(participant_orm: ParticipantModel) -> Participant:
        return Participant(
            id=participant_orm.id,
            equipo_id=participant_orm.equipo_id,
            nombres=participant_orm.nombres,
            apellidos=participant_orm.apellidos,
            edad=participant_orm.edad,
            grado_academico=participant_orm.grado_academico,
            documento_identidad=participant_orm.documento_identidad,
            autorizacion_datos=participant_orm.autorizacion_datos,
            rol_en_equipo=participant_orm.rol_en_equipo
        )

    @staticmethod
    def _team_to_domain(team_orm: TeamModel) -> Team:
        participants = [
            TeamRepositoryPostgresql._participant_to_domain(p)
            for p in team_orm.participants.all()
        ]
        return Team(
            id=team_orm.id,
            tournament_id=team_orm.torneo_id,
            name=team_orm.nombre,
            category=team_orm.categoria,
            institution_id=team_orm.institucion_id,
            nivel_tecnico_declarado=team_orm.nivel_tecnico_declarado,
            representante_id=team_orm.representante_id,
            docente_asesor_id=team_orm.docente_asesor_id,
            estado_inscripcion=team_orm.estado_inscripcion,
            fecha_inscripcion=team_orm.fecha_inscripcion,
            participants=participants
        )

    def save(self, team: Team):
        team_orm = TeamModel.objects.create(
            id=team.id,
            torneo_id=team.tournament_id,
            nombre=team.name,
            categoria=team.category,
            institucion_id=team.institution_id,
            nivel_tecnico_declarado=team.nivel_tecnico_declarado,
            estado_inscripcion=team.estado_inscripcion,
            fecha_inscripcion=team.fecha_inscripcion,
            representante_id=team.representante_id,
            docente_asesor_id=team.docente_asesor_id
        )
        for p in team.participants:
            ParticipantModel.objects.create(
                id=p.id,
                equipo=team_orm,
                nombres=p.nombres,
                apellidos=p.apellidos,
                edad=p.edad,
                grado_academico=p.grado_academico,
                documento_identidad=p.documento_identidad,
                autorizacion_datos=p.autorizacion_datos,
                rol_en_equipo=p.rol_en_equipo
            )

    def find_by_id(self, id: str) -> Team | None:
        try:
            team_orm = TeamModel.objects.prefetch_related('participants').get(pk=id)
            return self._team_to_domain(team_orm)
        except TeamModel.DoesNotExist:
            return None

    def find_all(self) -> list[Team]:
        teams_orm = TeamModel.objects.prefetch_related('participants').all()
        return [self._team_to_domain(t) for t in teams_orm]

    def delete(self, id: str):
        TeamModel.objects.filter(pk=id).delete()

    def update(self, team: Team):
        TeamModel.objects.filter(pk=team.id).update(
            nombre=team.name,
            categoria=team.category,
            estado_inscripcion=team.estado_inscripcion,
            nivel_tecnico_declarado=team.nivel_tecnico_declarado,
            docente_asesor_id=team.docente_asesor_id
        )
        # Sincronizar participantes
        team_orm = TeamModel.objects.get(pk=team.id)
        team_orm.participants.all().delete()
        for p in team.participants:
            ParticipantModel.objects.create(
                id=p.id,
                equipo=team_orm,
                nombres=p.nombres,
                apellidos=p.apellidos,
                edad=p.edad,
                grado_academico=p.grado_academico,
                documento_identidad=p.documento_identidad,
                autorizacion_datos=p.autorizacion_datos,
                rol_en_equipo=p.rol_en_equipo
            )

    def find_by_name(self, name: str) -> list[Team] | None:
        teams_orm = TeamModel.objects.filter(nombre__icontains=name)
        return [self._team_to_domain(t) for t in teams_orm]

    def find_by_creator_user(self, creator_user_id: str) -> list[Team]:
        # En este modelo, el creador es el representante
        teams_orm = TeamModel.objects.filter(representante_id=creator_user_id)
        return [self._team_to_domain(t) for t in teams_orm]

    def find_by_institution(self, institution_id: str) -> list[Team]:
        teams_orm = TeamModel.objects.filter(institucion_id=institution_id)
        return [self._team_to_domain(t) for t in teams_orm]

    def find_by_teacher(self, teacher_id: str) -> list[Team]:
        teams_orm = TeamModel.objects.filter(docente_asesor_id=teacher_id)
        return [self._team_to_domain(t) for t in teams_orm]
