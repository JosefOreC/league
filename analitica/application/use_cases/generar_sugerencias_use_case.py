from ...domain.ports.sugerencias_repository_port import ISugerenciasRepository
from ...domain.entities.sugerencia_decision import SugerenciaDecision
from ...domain.exceptions import TorneoNoEncontradoException


_MSG_SIN_ANOMALIAS = (
    "El torneo no presenta anomalías operativas ni académicas detectables. "
    "Sin acciones recomendadas."
)


class GenerarSugerenciasUseCase:
    """
    Orquesta HU-AN-05 — Sugerencias inteligentes de acción.
    Lógica 100% determinista, sin LLM.

    Reglas:
        REPROGRAMACION  → torneo en cualquier estado, >= 3 partidos retrasados > 20 min.
        AJUSTE_CRITERIO → solo si FINISHED, criterio con stddev > 40 o < 2.
        APOYO_EQUIPO    → solo si FINISHED, equipo en percentil <= 10.
    """

    def __init__(self, repository: ISugerenciasRepository) -> None:
        self._repo = repository

    def execute(self, torneo_id: str) -> dict:
        estado = self._repo.obtener_estado_torneo(torneo_id)
        if estado is None:
            raise TorneoNoEncontradoException(torneo_id)

        self._evaluar_reprogramacion(torneo_id)

        if (estado or '').lower() == 'finalized':
            self._evaluar_criterios(torneo_id)
            self._evaluar_equipos(torneo_id)

        pendientes = self._repo.obtener_pendientes(torneo_id)

        result: dict = {"torneo_id": torneo_id, "sugerencias": pendientes}
        if not pendientes:
            result["mensaje"] = _MSG_SIN_ANOMALIAS
        return result

    # ── evaluadores privados ──────────────────────────────────────────────────

    def _evaluar_reprogramacion(self, torneo_id: str) -> None:
        datos = self._repo.analizar_retrasos(torneo_id)
        if not datos:
            return
        total = datos[0]["total"]
        if total < 3:
            return
        self._repo.upsert_sugerencia(
            torneo_id=torneo_id,
            tipo="REPROGRAMACION",
            descripcion=(
                f"{total} partidos tienen retraso acumulado de más de 20 minutos. "
                "Se recomienda reprogramar los slots de la ronda actual."
            ),
            accion_sugerida=(
                "Extender fecha_programada de los partidos afectados en 30 minutos."
            ),
            entidad_ref_id="",
            severidad="WARNING",
        )

    def _evaluar_criterios(self, torneo_id: str) -> None:
        for c in self._repo.analizar_criterios(torneo_id):
            desv = c["desv_est"]
            if desv > 40:
                motivo = f"muy alta dispersión (desviación estándar: {desv:.1f})"
            else:
                motivo = f"muy baja variación entre equipos (desviación estándar: {desv:.1f})"
            self._repo.upsert_sugerencia(
                torneo_id=torneo_id,
                tipo="AJUSTE_CRITERIO",
                descripcion=(
                    f"El criterio '{c['criterio_nombre']}' tuvo {motivo}. "
                    "Considerar redefinir el rango o el peso para la próxima edición."
                ),
                accion_sugerida="",
                entidad_ref_id=c["criterio_id"],
                severidad="INFO",
            )

    def _evaluar_equipos(self, torneo_id: str) -> None:
        for eq in self._repo.analizar_equipos_bajo_rendimiento(torneo_id):
            criterios_txt = (
                ", ".join(eq["criterios_debiles"])
                if eq["criterios_debiles"]
                else "criterios evaluados"
            )
            self._repo.upsert_sugerencia(
                torneo_id=torneo_id,
                tipo="APOYO_EQUIPO",
                descripcion=(
                    f"El equipo '{eq['equipo_nombre']}' se encuentra en el 10% inferior "
                    f"de desempeño (puntaje: {eq['puntaje']:.2f}). "
                    "Se recomienda que el docente asesor programe sesiones de refuerzo "
                    f"en los criterios: {criterios_txt}."
                ),
                accion_sugerida=(
                    "Coordinar con el docente asesor sesiones de refuerzo técnico."
                ),
                entidad_ref_id=eq["equipo_id"],
                severidad="WARNING",
            )
