import uuid

from ...domain.entities.criterio_ia import CriterioIA
from ...domain.ports.rubrica_generator_port import RubricaGeneratorPort
from ...domain.ports.criterio_ia_repository_port import CriterioIARepositoryPort
from ...domain.value_objects.enums.tipo_torneo import TipoTorneo
from ...domain.value_objects.enums.nivel_tecnico import NivelTecnico
from ...domain.value_objects.enums.categoria import Categoria


_NIVEL_MAP: dict[int, NivelTecnico] = {
    1: NivelTecnico.BASICO,
    2: NivelTecnico.INTERMEDIO,
    3: NivelTecnico.AVANZADO,
}


class GenerarCriteriosIAUseCase:

    def __init__(
        self,
        generator: RubricaGeneratorPort,
        repository: CriterioIARepositoryPort,
    ) -> None:
        self._generator = generator
        self._repository = repository

    def execute(
        self,
        torneo_id: str,
        tipo_torneo: str,
        nivel: str | int,
        categoria: str,
    ) -> tuple[str, list[CriterioIA]]:
        """
        Genera y persiste los criterios de evaluación para un torneo.

        Retorna (sesion_ia_id, lista_de_criterios).
        """
        tipo  = self._parse_tipo_torneo(tipo_torneo)
        niv   = self._parse_nivel(nivel)
        cat   = self._parse_categoria(categoria)

        sesion_ia_id = str(uuid.uuid4())
        criterios = self._generator.generar(
            torneo_id=torneo_id,
            sesion_ia_id=sesion_ia_id,
            tipo_torneo=tipo,
            nivel=niv,
            categoria=cat,
        )
        self._repository.save_all(criterios)
        return sesion_ia_id, criterios

    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_tipo_torneo(value: str) -> TipoTorneo:
        try:
            return TipoTorneo(value.upper())
        except (ValueError, AttributeError):
            valid = [e.value for e in TipoTorneo]
            raise ValueError(f"tipo_torneo inválido. Valores permitidos: {valid}")

    @staticmethod
    def _parse_nivel(value: str | int) -> NivelTecnico:
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            mapped = _NIVEL_MAP.get(int(value))
            if mapped is None:
                raise ValueError("nivel numérico debe ser 1 (BASICO), 2 (INTERMEDIO) o 3 (AVANZADO)")
            return mapped
        try:
            return NivelTecnico(str(value).upper())
        except ValueError:
            valid = [e.value for e in NivelTecnico]
            raise ValueError(f"nivel inválido. Valores permitidos: {valid} o 1/2/3")

    @staticmethod
    def _parse_categoria(value: str) -> Categoria:
        try:
            return Categoria(value.upper())
        except (ValueError, AttributeError):
            valid = [e.value for e in Categoria]
            raise ValueError(f"categoria inválida. Valores permitidos: {valid}")
