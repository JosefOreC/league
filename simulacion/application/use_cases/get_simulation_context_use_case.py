"""
Caso de uso: GetSimulationContextUseCase — HU-SIM-01.

Orquesta la lógica de aplicación para recuperar el contexto de simulación
(torneo + equipo + criterios) de un representante autorizado.
"""
from typing import Optional

from simulacion.domain.entities.simulation_context import SimulationContext
from simulacion.domain.ports.tournament_context_port import TournamentContextPort


class TournamentNotFoundError(Exception):
    """Se lanza cuando el tournament_id no existe en la base de datos."""
    pass


class TeamNotApprovedError(Exception):
    """
    Se lanza cuando el torneo existe pero el user_id del JWT no es
    representante_id de ningún equipo con estado_inscripcion='APROBADO'.
    """
    pass


class GetSimulationContextUseCase:
    """
    Caso de uso HU-SIM-01 — Obtener contexto de simulación del torneo.

    El caso de uso es agnóstico a la persistencia; recibe el port (interfaz)
    por inyección de dependencias para garantizar la testabilidad con mocks.
    """

    def __init__(self, tournament_context_port: TournamentContextPort):
        self._port = tournament_context_port

    def execute(
        self,
        tournament_id: str,
        representante_id: str,
    ) -> SimulationContext:
        """
        Ejecuta el caso de uso.

        Args:
            tournament_id: ID del torneo objetivo.
            representante_id: user_id extraído del JWT (campo 'user_id' del payload).

        Returns:
            SimulationContext con tournament, team y criterios.

        Raises:
            TournamentNotFoundError: si el torneo no existe (→ HTTP 404).
            TeamNotApprovedError: si el representante no tiene equipo aprobado (→ HTTP 403).
        """
        context: Optional[SimulationContext] = self._port.get_context(
            tournament_id=tournament_id,
            representante_id=representante_id,
        )

        if context is None:
            raise TournamentNotFoundError(
                f"Torneo con id '{tournament_id}' no encontrado."
            )

        return context
