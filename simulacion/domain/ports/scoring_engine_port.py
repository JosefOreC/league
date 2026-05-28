"""
Puerto (interfaz) del dominio para el motor de scoring.
Define el contrato que la implementación heurística debe cumplir.
"""
from abc import ABC, abstractmethod

from simulacion.domain.entities.simulation_context import SimulationContext
from simulacion.domain.entities.simulation_result import SimulationResult


class ScoringEnginePort(ABC):
    """
    Puerto de salida (driven port) para calcular la calificación simulada
    de un entregable textual contra los criterios de un torneo.

    La implementación concreta (HeuristicScoringEngine) reside en
    simulacion/infrastructure/scoring/ y puede ser sustituida por
    cualquier otro motor (ML, LLM, etc.) sin afectar al dominio.
    """

    @abstractmethod
    def score(
        self,
        entregable: str,
        context: SimulationContext,
    ) -> SimulationResult:
        """
        Calcula el resultado de la simulación.

        Args:
            entregable: Texto descriptivo del entregable del equipo (≥100 chars).
            context:    SimulationContext con torneo, equipo y criterios, incluyendo
                        total_approved_teams para el cálculo de posición.

        Returns:
            SimulationResult con scores, puntaje_total, posición, fortalezas,
            debilidades y retroalimentación.
        """
        ...
