from ....domain.ports.institution_repository import InstitutionRepository
from ....domain.entities.institution import Institution
from ...adapters.output.models import InstitutionModel

class InstitutionRepositoryPostgresql(InstitutionRepository):
    
    @staticmethod
    def _institution_to_domain(institution_orm: InstitutionModel) -> Institution:
        return Institution(
            id=institution_orm.id,
            name=institution_orm.name,
            type=institution_orm.type,
            city=institution_orm.city,
            country=institution_orm.country
        )

    def save(self, institution: Institution):
        InstitutionModel.objects.update_or_create(
            id=institution.id,
            defaults={
                "name": institution.name,
                "type": institution.type,
                "city": institution.city,
                "country": institution.country
            }
        )

    def find_by_id(self, id: str) -> Institution | None:
        try:
            institution_orm = InstitutionModel.objects.get(pk=id)
            return self._institution_to_domain(institution_orm)
        except InstitutionModel.DoesNotExist:
            return None

    def find_all(self) -> list[Institution]:
        institutions_orm = InstitutionModel.objects.all()
        return [self._institution_to_domain(i) for i in institutions_orm]

    def delete(self, id: str):
        InstitutionModel.objects.filter(pk=id).delete()

    def update(self, institution: Institution):
        self.save(institution)

    def find_by_name(self, name: str) -> Institution | None:
        try:
            institution_orm = InstitutionModel.objects.filter(name__iexact=name).first()
            if institution_orm:
                return self._institution_to_domain(institution_orm)
            return None
        except Exception:
            return None

    def find_by_city(self, city: str) -> list[Institution]:
        institutions_orm = InstitutionModel.objects.filter(city__icontains=city)
        return [self._institution_to_domain(i) for i in institutions_orm]
