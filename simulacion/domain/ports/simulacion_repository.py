from abc import ABC, abstractmethod
from typing import List

from simulacion.domain.entities.simulacion_predictiva import SimulacionPredictivaEntity


class SimulacionRepositoryPort(ABC):

    @abstractmethod
    def guardar(self, entidad: SimulacionPredictivaEntity):
        raise NotImplementedError

    @abstractmethod
    def obtener_historial(self, participante_id: int) -> List[dict]:
        raise NotImplementedError
