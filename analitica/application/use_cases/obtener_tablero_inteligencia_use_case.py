"""
Use Case: ObtenerTableroInteligenciaUseCase — HU-AN-04
Capa: application/
Importa SOLO interfaces del domain/. NO importa nada de infrastructure/.
"""
from ...domain.ports.tablero_inteligencia_repository_port import ITableroInteligenciaRepository
from ...domain.entities.tablero_inteligencia import TableroInteligencia
from ...domain.exceptions import (
    TorneoNoEncontradoException,
    AccesoNoAutorizadoException,
)

# Estados en los que el tablero está disponible (no solo finalized)
ESTADOS_TABLERO_VALIDOS = {"IN_PROGRESS", "finalized"}


class ObtenerTableroInteligenciaUseCase:
    """
    Orquesta la validación de precondiciones y la obtención del tablero
    de inteligencia del organizador.

    Reglas de negocio (HU-AN-04):
        1. El torneo debe existir.
        2. El torneo debe estar en estado IN_PROGRESS o finalized.
           (A diferencia de HU-AN-01, NO se restringe a solo finalized)
        3. Solo ADMIN o MANAGER pueden acceder al tablero.
    """

    def __init__(self, repository: ITableroInteligenciaRepository) -> None:
        self._repo = repository

    def execute(self, torneo_id: str) -> TableroInteligencia:
        """
        Retorna el tablero de inteligencia del torneo.

        Args:
            torneo_id: UUID del torneo.

        Returns:
            TableroInteligencia con métricas, top-3 y alertas activas.

        Raises:
            TorneoNoEncontradoException: Si el torneo no existe (→ 404).
            AccesoNoAutorizadoException: Si el estado no permite el tablero (→ 409).
                                         (DRAFT no tiene datos significativos)
        """
        estado = self._repo.obtener_estado_torneo(torneo_id)
        if estado is None:
            raise TorneoNoEncontradoException(torneo_id)

        if estado not in ESTADOS_TABLERO_VALIDOS:
            # DRAFT: el torneo aún no ha comenzado, no hay datos de partidos
            raise AccesoNoAutorizadoException(
                f"El tablero de inteligencia solo está disponible cuando el torneo "
                f"está en estado IN_PROGRESS o finalized. Estado actual: '{estado}'."
            )

        tablero = self._repo.obtener_tablero(torneo_id)
        if tablero is None:
            raise TorneoNoEncontradoException(torneo_id)

        return tablero
