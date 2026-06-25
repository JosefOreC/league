"""
Use Case: ObtenerAnalisisIntegralUseCase — HU-AN-01
Capa: application/
Importa SOLO interfaces del domain/. NO importa nada de infrastructure/.
"""
from typing import Optional
from ...domain.ports.analisis_integral_repository_port import IAnalisisIntegralRepository
from ...domain.entities.analisis_integral import AnalisisIntegral
from ...domain.exceptions import (
    TorneoNoEncontradoException,
    TorneoNoFinalizadoException,
    SinResultadosDefinitivosException,
)

# Categorías válidas para el filtro opcional
CATEGORIAS_VALIDAS = {"PRIMARY", "SECONDARY"}


class ObtenerAnalisisIntegralUseCase:
    """
    Orquesta la validación de precondiciones y la obtención del análisis integral.

    Reglas de negocio:
        1. El torneo debe existir.
        2. El torneo debe estar en estado 'finalized'.
        3. Deben existir resultados con estado 'DEFINITIVO'.
        4. (Opcional) Si se pasa `categoria`, filtra equipos de esa categoría.
    """

    def __init__(self, repository: IAnalisisIntegralRepository) -> None:
        self._repo = repository

    def execute(
        self,
        torneo_id: str,
        categoria: Optional[str] = None,
    ) -> AnalisisIntegral:
        """
        Ejecuta el análisis integral del torneo.

        Args:
            torneo_id: UUID del torneo a analizar.
            categoria: Filtro opcional ('PRIMARY' | 'SECONDARY').

        Returns:
            AnalisisIntegral con todas las métricas calculadas.

        Raises:
            TorneoNoEncontradoException: Si el torneo no existe (→ 404).
            TorneoNoFinalizadoException: Si el torneo no está finalized (→ 409).
            SinResultadosDefinitivosException: Si no hay resultados DEFINITIVO (→ 422).
        """
        # Normalizar categoría
        categoria_normalizada: Optional[str] = None
        if categoria:
            categoria_normalizada = categoria.upper()
            if categoria_normalizada not in CATEGORIAS_VALIDAS:
                categoria_normalizada = None  # Ignora valores inválidos silenciosamente

        # 1. Verificar existencia del torneo
        estado = self._repo.obtener_estado_torneo(torneo_id)
        if estado is None:
            raise TorneoNoEncontradoException(torneo_id)

        # 2. Verificar que el torneo está finalized
        if estado != "finalized":
            raise TorneoNoFinalizadoException(torneo_id, estado)

        # 3. Obtener análisis (la query detecta si hay resultados DEFINITIVO)
        analisis = self._repo.obtener_analisis(torneo_id, categoria_normalizada)

        # 4. Verificar que hay resultados DEFINITIVO
        if analisis is None:
            raise SinResultadosDefinitivosException(torneo_id)

        return analisis
