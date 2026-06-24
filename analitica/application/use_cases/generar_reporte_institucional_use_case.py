from typing import Optional, Union
from ...domain.ports.reporte_institucional_repository_port import IReporteInstitucionalRepository
from ...domain.entities.reporte_institucional import ReporteInstitucional, ReporteInstitucionalHistorico
from ...domain.exceptions import (
    TorneoNoEncontradoException,
    TorneoNoFinalizadoException,
    InstitucionSinEquiposException,
)


class GenerarReporteInstitucionalUseCase:
    """
    Orquesta HU-AN-03.
    Reglas de negocio:
        1. Si se pide torneo específico: el torneo debe existir y estar en FINISHED.
        2. Si la institución no tiene equipos APROBADO en el torneo → 404.
        3. Si historico=True: retorna todos los torneos FINISHED donde participó.
        4. Si no hay histórico → 404 con InstitucionSinEquiposException.
    """

    def __init__(self, repository: IReporteInstitucionalRepository) -> None:
        self._repo = repository

    def execute(
        self,
        inst_id: str,
        torneo_id: Optional[str] = None,
        historico: bool = False,
    ) -> Union[ReporteInstitucional, ReporteInstitucionalHistorico]:

        if historico:
            resultado = self._repo.obtener_reporte_historico(inst_id)
            if resultado is None:
                raise InstitucionSinEquiposException(inst_id, 'histórico')
            return resultado

        estado = self._repo.obtener_estado_torneo(torneo_id)
        if estado is None:
            raise TorneoNoEncontradoException(torneo_id)
        if (estado or '').lower() != 'finalized':
            raise TorneoNoFinalizadoException(torneo_id, estado)

        reporte = self._repo.obtener_reporte_torneo(inst_id, torneo_id)
        if reporte is None:
            raise InstitucionSinEquiposException(inst_id, torneo_id)

        return reporte
