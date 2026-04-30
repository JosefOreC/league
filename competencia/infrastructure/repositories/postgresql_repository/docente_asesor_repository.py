from ....domain.ports.docente_asesor_repository import DocenteAsesorRepository
from ....domain.entities.docente_asesor import DocenteAsesor
from ...adapters.output.models import DocenteAsesorModel, InstitutionModel

class DocenteAsesorRepositoryPostgresql(DocenteAsesorRepository):
    
    @staticmethod
    def _docente_to_domain(docente_orm: DocenteAsesorModel) -> DocenteAsesor:
        return DocenteAsesor(
            id=docente_orm.id,
            nombre_completo=docente_orm.nombre_completo,
            email=docente_orm.email,
            telefono=docente_orm.telefono,
            institution_id=docente_orm.institution_id
        )

    def save(self, docente: DocenteAsesor):
        institution = InstitutionModel.objects.get(pk=docente.institution_id)
        DocenteAsesorModel.objects.update_or_create(
            id=docente.id,
            defaults={
                "nombre_completo": docente.nombre_completo,
                "email": docente.email,
                "telefono": docente.telefono,
                "institution": institution
            }
        )

    def find_by_id(self, id: str) -> DocenteAsesor | None:
        try:
            docente_orm = DocenteAsesorModel.objects.get(pk=id)
            return self._docente_to_domain(docente_orm)
        except DocenteAsesorModel.DoesNotExist:
            return None

    def find_by_email(self, email: str) -> DocenteAsesor | None:
        try:
            docente_orm = DocenteAsesorModel.objects.get(email=email)
            return self._docente_to_domain(docente_orm)
        except DocenteAsesorModel.DoesNotExist:
            return None
