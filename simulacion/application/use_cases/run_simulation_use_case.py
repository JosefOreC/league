"""
Caso de uso: RunSimulationUseCase — HU-SIM-02 (+ HU-SIM-03, 04, 05).

Orquesta:
  1. Validación del entregable (longitud mínima).
  2. Recuperación del contexto de simulación (delega a TournamentContextPort).
  3. Cálculo del scoring (delega a ScoringEnginePort).
  4. Retorno del SimulationResult completo.
"""
from simulacion.application.use_cases.get_simulation_context_use_case import (
    TeamNotApprovedError,       # re-exportado para uso en la vista
    TournamentNotFoundError,    # re-exportado para uso en la vista
)
from simulacion.domain.entities.simulation_result import SimulationResult
from simulacion.domain.ports.scoring_engine_port import ScoringEnginePort
from simulacion.domain.ports.tournament_context_port import TournamentContextPort

MIN_ENTREGABLE_LENGTH = 100


class EntregableDemasiadoCortoError(Exception):
    """El texto del entregable no alcanza el mínimo de caracteres requerido."""
    def __init__(self, actual_length: int):
        self.actual_length = actual_length
        super().__init__(
            f"El entregable debe tener al menos {MIN_ENTREGABLE_LENGTH} caracteres"
        )


class EntregableAusenteError(Exception):
    """El campo 'entregable' no fue enviado o está vacío."""
    pass


class RunSimulationUseCase:
    """
    Caso de uso HU-SIM-02 — Ejecutar simulación predictiva.

    Depende de dos ports inyectados:
      - tournament_context_port: recupera torneo + equipo + criterios (HU-SIM-01).
      - scoring_engine_port:     calcula scores, posición, fortalezas y feedback.
    """

    def __init__(
        self,
        tournament_context_port: TournamentContextPort,
        scoring_engine_port: ScoringEnginePort,
    ):
        self._context_port = tournament_context_port
        self._engine = scoring_engine_port

    def execute(
        self,
        tournament_id: str,
        representante_id: str,
        entregable: str | None,
    ) -> SimulationResult:
        """
        Ejecuta la simulación completa.

        Args:
            tournament_id:    ID del torneo.
            representante_id: user_id del JWT.
            entregable:       Texto del entregable (puede ser None o vacío).

        Returns:
            SimulationResult completo (HU-SIM-02 a HU-SIM-05).

        Raises:
            EntregableAusenteError:       campo faltante o vacío  → HTTP 400.
            EntregableDemasiadoCortoError: < 100 caracteres        → HTTP 400.
            TournamentNotFoundError:      torneo no existe         → HTTP 404.
            TeamNotApprovedError:         sin equipo aprobado      → HTTP 403.
        """
        # --- Validación 1: campo presente ---
        if not entregable:
            raise EntregableAusenteError("El campo 'entregable' es requerido")

        # --- Validación 2: longitud mínima ---
        if len(entregable) < MIN_ENTREGABLE_LENGTH:
            raise EntregableDemasiadoCortoError(actual_length=len(entregable))

        # --- Obtener contexto (reutiliza HU-SIM-01 port) ---
        context = self._context_port.get_context(
            tournament_id=tournament_id,
            representante_id=representante_id,
        )

        if context is None:
            raise TournamentNotFoundError(
                f"Torneo con id '{tournament_id}' no encontrado."
            )

        # --- Ejecutar motor de scoring ---
        return self._engine.score(entregable=entregable, context=context)
