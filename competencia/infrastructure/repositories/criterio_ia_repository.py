from decimal import Decimal

from ...domain.entities.criterio_ia import CriterioIA
from ...domain.ports.criterio_ia_repository_port import CriterioIARepositoryPort
from ...domain.value_objects.enums.tipo_dato import TipoDato
from ...domain.value_objects.enums.estado_criterio import EstadoCriterio


class CriterioIARepository(CriterioIARepositoryPort):

    # ------------------------------------------------------------------ #
    # Mappers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_domain(orm) -> CriterioIA:
        return CriterioIA(
            id=str(orm.id),
            torneo_id=orm.torneo_id,
            sesion_ia_id=orm.sesion_ia_id,
            nombre=orm.nombre,
            descripcion=orm.descripcion,
            tipo_dato=TipoDato(orm.tipo_dato),
            peso_porcentual=Decimal(str(orm.peso_porcentual)),
            valor_minimo=Decimal(str(orm.valor_minimo)) if orm.valor_minimo is not None else None,
            valor_maximo=Decimal(str(orm.valor_maximo)) if orm.valor_maximo is not None else None,
            mayor_es_mejor=orm.mayor_es_mejor,
            orden=orm.orden,
            estado=EstadoCriterio(orm.estado),
        )

    @staticmethod
    def _model_class():
        from ..adapters.output.models import CriterioIAModel
        return CriterioIAModel

    # ------------------------------------------------------------------ #
    # Puerto                                                               #
    # ------------------------------------------------------------------ #

    def save_all(self, criterios: list[CriterioIA]) -> None:
        Model = self._model_class()
        Model.objects.bulk_create([
            Model(
                id=c.id,
                torneo_id=c.torneo_id,
                sesion_ia_id=c.sesion_ia_id,
                nombre=c.nombre,
                descripcion=c.descripcion,
                tipo_dato=c.tipo_dato.value,
                peso_porcentual=c.peso_porcentual,
                valor_minimo=c.valor_minimo,
                valor_maximo=c.valor_maximo,
                mayor_es_mejor=c.mayor_es_mejor,
                orden=c.orden,
                estado=c.estado.value,
            )
            for c in criterios
        ])

    def find_by_sesion(self, sesion_ia_id: str) -> list[CriterioIA]:
        Model = self._model_class()
        return [
            self._to_domain(orm)
            for orm in Model.objects.filter(sesion_ia_id=sesion_ia_id).order_by("orden")
        ]

    def find_by_id(self, criterio_id: str) -> CriterioIA | None:
        Model = self._model_class()
        try:
            return self._to_domain(Model.objects.get(id=criterio_id))
        except Model.DoesNotExist:
            return None

    def update(self, criterio: CriterioIA) -> None:
        Model = self._model_class()
        Model.objects.filter(id=criterio.id).update(
            peso_porcentual=criterio.peso_porcentual,
            estado=criterio.estado.value,
        )

    def update_all(self, criterios: list[CriterioIA]) -> None:
        for c in criterios:
            self.update(c)
