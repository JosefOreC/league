"""
Use Case: ObtenerPanelDocenteUseCase — HU-AN-08
Capa: application/
Importa SOLO interfaces del domain/. NO importa nada de infrastructure/.
"""
from typing import Optional
from ...domain.ports.panel_docente_repository_port import IPanelDocenteRepository
from ...domain.services.recomendaciones_pedagogicas_service import (
    RecomendacionesPedagogicasService,
)
from ...domain.entities.panel_docente import (
    PanelDocente,
    EstadoPanel,
)
from ...domain.exceptions import (
    TorneoNoEncontradoException,
    EquipoNoEncontradoException,
    DocenteNoVinculadoException,
    AccesoNoAutorizadoException,
)

# Mínimo de partidos finalized para emitir un panel PRELIMINAR
MIN_PARTIDOS_PANEL_PRELIMINAR = 2

ADVERTENCIA_PRELIMINAR = (
    "Este panel es PRELIMINAR. Los datos están basados en partidos ya finalizados "
    "pero el torneo aún está en curso. Las recomendaciones pueden cambiar al cierre del torneo."
)


class ObtenerPanelDocenteUseCase:
    """
    Orquesta la validación de precondiciones y la generación del panel docente.

    Reglas de negocio (HU-AN-08):
        1. El torneo debe existir.
        2. El equipo debe pertenecer al torneo.
        3. El usuario solicitante debe ser el docente_asesor vinculado al equipo
           (o ADMIN/MANAGER para supervisión).
        4. Si el torneo está IN_PROGRESS con ≥ 2 partidos finalized:
           → Retorna panel con estado_panel = PRELIMINAR y advertencia.
        5. Si el torneo está finalized:
           → Retorna panel con estado_panel = DEFINITIVO.
        6. Si el torneo está DRAFT o IN_PROGRESS con < 2 partidos finalized:
           → Error 403 (datos insuficientes).
        7. El domain service de recomendaciones es invocado desde aquí (no desde infra).
    """

    def __init__(
        self,
        repository: IPanelDocenteRepository,
        recomendaciones_service: Optional[RecomendacionesPedagogicasService] = None,
    ) -> None:
        self._repo = repository
        self._rec_service = recomendaciones_service or RecomendacionesPedagogicasService()

    def execute(
        self,
        torneo_id: str,
        equipo_id: str,
        usuario_id: str,
        usuario_rol: str,
    ) -> PanelDocente:
        """
        Genera el panel de retroalimentación para el docente asesor del equipo.

        Args:
            torneo_id:    UUID del torneo.
            equipo_id:    UUID del equipo.
            usuario_id:   UUID del usuario que hace la solicitud (del JWT).
            usuario_rol:  Rol del usuario ('admin', 'manager', 'coach', 'participant').

        Returns:
            PanelDocente con recomendaciones pedagógicas.

        Raises:
            TorneoNoEncontradoException:  Si el torneo no existe (→ 404).
            EquipoNoEncontradoException:  Si el equipo no pertenece al torneo (→ 404).
            DocenteNoVinculadoException:  Si el docente no está vinculado al equipo (→ 403).
            AccesoNoAutorizadoException:  Si el torneo está en DRAFT o sin datos (→ 403).
        """
        # 1. Verificar existencia del torneo
        estado = self._repo.obtener_estado_torneo(torneo_id)
        if estado is None:
            raise TorneoNoEncontradoException(torneo_id)

        # 2. Verificar que el equipo pertenece al torneo
        if not self._repo.equipo_pertenece_a_torneo(equipo_id, torneo_id):
            raise EquipoNoEncontradoException(equipo_id, torneo_id)

        # 3. Validar acceso: solo docente_asesor del equipo (o ADMIN/MANAGER)
        rol_upper = usuario_rol.upper()
        docente_id = None
        docente_nombre = ""

        if rol_upper not in ("ADMIN", "MANAGER"):
            docente_info = self._repo.obtener_docente_del_equipo(equipo_id)
            if docente_info is None:
                raise EquipoNoEncontradoException(equipo_id, torneo_id)

            docente_id_bd, docente_nombre_bd = docente_info

            if str(usuario_id) != str(docente_id_bd):
                raise DocenteNoVinculadoException(usuario_id, equipo_id)

            docente_id = docente_id_bd
            docente_nombre = docente_nombre_bd
        else:
            # Admin/Manager: obtener info del docente para incluirla en el panel
            docente_info = self._repo.obtener_docente_del_equipo(equipo_id)
            if docente_info:
                docente_id, docente_nombre = docente_info

        # 4. Determinar estado del panel
        estado_panel, advertencia = self._determinar_estado_panel(torneo_id, estado)

        # 5. Obtener criterios con percentil
        criterios = self._repo.obtener_criterios_con_percentil(torneo_id, equipo_id)

        # 6. Generar recomendaciones (lógica de dominio puro)
        recomendaciones = self._rec_service.generar_recomendaciones(criterios)

        # 7. Datos base del equipo
        info = self._repo.obtener_info_equipo_panel(torneo_id, equipo_id)

        return PanelDocente(
            torneo_id=torneo_id,
            torneo_nombre=info["torneo_nombre"] if info else "",
            equipo_id=equipo_id,
            equipo_nombre=info["equipo_nombre"] if info else "",
            docente_asesor_id=str(docente_id) if docente_id else "",
            docente_nombre=docente_nombre,
            estado_panel=estado_panel,
            advertencia=advertencia,
            posicion_final=info["posicion_final"] if info else None,
            medalla=info["medalla"] if info else None,
            puntaje_total_acumulado=info["puntaje_total_acumulado"] if info else 0.0,
            total_partidos_jugados=info["total_partidos_jugados"] if info else 0,
            criterios=criterios,
            recomendaciones=recomendaciones,
        )

    def _determinar_estado_panel(
        self, torneo_id: str, estado_torneo: str
    ) -> tuple[EstadoPanel, Optional[str]]:
        """
        Determina si el panel es PRELIMINAR o DEFINITIVO y genera el mensaje.

        Returns:
            Tupla (EstadoPanel, advertencia_o_None)

        Raises:
            AccesoNoAutorizadoException si el torneo está en DRAFT o
            IN_PROGRESS con menos de 2 partidos finalizados.
        """
        if estado_torneo == "finalized":
            return EstadoPanel.DEFINITIVO, None

        if estado_torneo == "IN_PROGRESS":
            partidos_finalizados = self._repo.contar_partidos_finalizados(torneo_id)
            if partidos_finalizados >= MIN_PARTIDOS_PANEL_PRELIMINAR:
                return EstadoPanel.PRELIMINAR, ADVERTENCIA_PRELIMINAR
            else:
                raise AccesoNoAutorizadoException(
                    f"El panel preliminar requiere al menos {MIN_PARTIDOS_PANEL_PRELIMINAR} "
                    f"partidos finalizados. Actualmente hay {partidos_finalizados}."
                )

        # DRAFT u otro estado
        raise AccesoNoAutorizadoException(
            f"El panel docente no está disponible cuando el torneo está en estado '{estado_torneo}'."
        )
