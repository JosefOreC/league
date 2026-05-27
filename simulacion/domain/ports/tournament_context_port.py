"""
Puerto (interfaz) del dominio para recuperar el contexto de simulación.
Define el contrato que el repositorio de infraestructura debe implementar.
"""
from abc import ABC, abstractmethod
from typing import Optional

from simulacion.domain.entities.simulation_context import SimulationContext


class TournamentContextPort(ABC):
    """
    Puerto de salida (driven port) para obtener el contexto de un torneo.

    La implementación concreta (TournamentContextRepository) reside en la capa
    de infraestructura y puede ser sustituida sin afectar al dominio ni a los
    casos de uso.
    """

    @abstractmethod
    def get_context(
        self,
        tournament_id: str,
        representante_id: str,
    ) -> Optional[SimulationContext]:
        """
        Recupera el contexto de simulación completo para un torneo y su representante.

        Args:
            tournament_id: PK del torneo.
            representante_id: user_id del JWT (debe coincidir con representante_id
                              del TeamModel con estado_inscripcion='APROBADO').

        Returns:
            SimulationContext si existe el torneo y el equipo aprobado.
            None si el torneo no existe.

        Raises:
            PermissionError: si el torneo existe pero el representante no tiene
                             un equipo aprobado en él.
        """
        ...
