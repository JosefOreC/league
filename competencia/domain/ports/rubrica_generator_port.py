from abc import ABC, abstractmethod
from ..entities.criterio_ia import CriterioIA
from ..value_objects.enums.tipo_torneo import TipoTorneo
from ..value_objects.enums.nivel_tecnico import NivelTecnico
from ..value_objects.enums.categoria import Categoria


class RubricaGeneratorPort(ABC):
    """
    Puerto de salida: genera una lista de CriterioIA cuya suma de
    peso_porcentual es exactamente 100.00%.
    """

    @abstractmethod
    def generar(
        self,
        torneo_id: str,
        sesion_ia_id: str,
        tipo_torneo: TipoTorneo,
        nivel: NivelTecnico,
        categoria: Categoria,
    ) -> list[CriterioIA]: ...
