"""
Use Case: GenerarReporteIndividualUseCase — HU-AN-02
Capa: application/
Importa SOLO interfaces del domain/. NO importa nada de infrastructure/.
"""
from typing import Optional
from ...domain.ports.reporte_individual_repository_port import IReporteIndividualRepository
from ...domain.entities.reporte_individual import ReporteIndividual
from ...domain.exceptions import (
    TorneoNoEncontradoException,
    TorneoNoFinalizadoException,
    EquipoNoEncontradoException,
    SinResultadosDefinitivosException,
    AccesoNoAutorizadoException,
)


class GenerarReporteIndividualUseCase:
    """
    Orquesta la validación de precondiciones y la obtención del reporte
    de desempeño individual de un equipo.

    Reglas de negocio (HU-AN-02):
        1. El torneo debe existir.
        2. El torneo debe estar en estado 'finalized'.
        3. El equipo debe pertenecer al torneo.
        4. El usuario solicitante debe ser representante o docente_asesor del equipo.
        5. Deben existir resultados con estado 'DEFINITIVO' para el equipo.
    """

    def __init__(self, repository: IReporteIndividualRepository) -> None:
        self._repo = repository

    def execute(
        self,
        torneo_id: str,
        equipo_id: str,
        usuario_id: str,
        usuario_rol: str,
    ) -> ReporteIndividual:
        """
        Genera el reporte individual del equipo.

        Args:
            torneo_id:    UUID del torneo.
            equipo_id:    UUID del equipo.
            usuario_id:   UUID del usuario que hace la solicitud (del JWT).
            usuario_rol:  Rol del usuario en el sistema (del JWT).

        Returns:
            ReporteIndividual con todas las métricas calculadas.

        Raises:
            TorneoNoEncontradoException:       Si el torneo no existe (→ 404).
            TorneoNoFinalizadoException:       Si el torneo no está finalized (→ 409).
            EquipoNoEncontradoException:       Si el equipo no pertenece al torneo (→ 404).
            AccesoNoAutorizadoException:       Si el usuario no tiene acceso al equipo (→ 403).
            SinResultadosDefinitivosException: Si no hay resultados DEFINITIVO (→ 422).
        """
        # 1. Verificar existencia y estado del torneo
        estado = self._repo.obtener_estado_torneo(torneo_id)
        if estado is None:
            raise TorneoNoEncontradoException(torneo_id)
        if estado != "finalized":
            raise TorneoNoFinalizadoException(torneo_id, estado)

        # 2. Verificar que el equipo pertenece al torneo
        if not self._repo.equipo_pertenece_a_torneo(equipo_id, torneo_id):
            raise EquipoNoEncontradoException(equipo_id, torneo_id)

        # 3. Verificar acceso por rol
        #    ADMIN y MANAGER pueden ver cualquier reporte.
        #    COACH y PARTICIPANT solo pueden ver el reporte de su propio equipo.
        rol_upper = usuario_rol.upper()
        if rol_upper not in ("ADMIN", "MANAGER"):
            vinculo = self._repo.obtener_representante_y_docente(equipo_id)
            if vinculo is None:
                raise EquipoNoEncontradoException(equipo_id, torneo_id)

            representante_id, docente_asesor_id = vinculo
            if usuario_id not in (representante_id, docente_asesor_id):
                raise AccesoNoAutorizadoException(
                    "Solo el representante o el docente asesor del equipo pueden ver este reporte."
                )

        # 4. Obtener el reporte
        reporte = self._repo.obtener_reporte(torneo_id, equipo_id)
        if reporte is None:
            raise SinResultadosDefinitivosException(torneo_id)

        return reporte
