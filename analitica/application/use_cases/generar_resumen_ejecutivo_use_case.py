from dataclasses import replace

from ...domain.ports.resumen_ejecutivo_repository_port import IResumenEjecutivoRepository
from ...domain.ports.sugerencias_repository_port import ISugerenciasRepository
from ...domain.entities.resumen_ejecutivo import ResumenEjecutivo
from ...domain.services.generador_resumen_service import generar_resumen
from ...domain.exceptions import (
    TorneoNoEncontradoException,
    TorneoNoFinalizadoException,
    SinResultadosDefinitivosException,
)

_TONOS_VALIDOS = {'FORMAL', 'DIVULGATIVO', 'CELEBRATORIO'}


class GenerarResumenEjecutivoUseCase:
    """
    Orquesta HU-AN-07 — Resumen ejecutivo narrativo del torneo.
    Generación determinista por plantillas (NLG), sin LLM externo.

    Reglas de negocio:
        1. El torneo debe existir.
        2. El torneo debe estar en estado finalized.
        3. Deben existir resultados DEFINITIVE → si no, 422.
        4. Las recomendaciones se obtienen del análisis de sugerencias (RF3-005).
        5. Cada generación incrementa la versión; las anteriores se conservan.
    """

    def __init__(
        self,
        repository: IResumenEjecutivoRepository,
        sugerencias_repository: ISugerenciasRepository,
    ) -> None:
        self._repo = repository
        self._sug_repo = sugerencias_repository

    def execute(self, torneo_id: str, tono: str = 'DIVULGATIVO') -> ResumenEjecutivo:
        tono = (tono or 'DIVULGATIVO').upper()
        if tono not in _TONOS_VALIDOS:
            tono = 'DIVULGATIVO'

        estado = self._repo.obtener_estado_torneo(torneo_id)
        if estado is None:
            raise TorneoNoEncontradoException(torneo_id)
        if (estado or '').lower() != 'finalized':
            raise TorneoNoFinalizadoException(torneo_id, estado)

        if not self._repo.existen_resultados_definitivos(torneo_id):
            raise SinResultadosDefinitivosException(torneo_id)

        metricas = self._repo.obtener_metricas(torneo_id)
        if metricas is None:
            raise SinResultadosDefinitivosException(torneo_id)

        # Recomendaciones desde RF3-005 (análisis de criterios y equipos).
        recomendaciones = self._obtener_recomendaciones(torneo_id)
        metricas = replace(metricas, recomendaciones=recomendaciones)

        texto = generar_resumen(metricas, tono)

        metricas_usadas = {
            'total_equipos':        metricas.total_equipos,
            'total_instituciones':  metricas.total_instituciones,
            'total_participantes':  metricas.total_participantes,
            'campeon_nombre':       metricas.campeon.nombre if metricas.campeon else '',
            'puntaje_campeon':      round(metricas.campeon.puntaje, 2) if metricas.campeon else 0.0,
        }

        version = self._repo.siguiente_version(torneo_id)
        return self._repo.guardar(
            torneo_id=torneo_id,
            resumen_texto=texto,
            tono=tono,
            version=version,
            metricas_usadas=metricas_usadas,
        )

    def _obtener_recomendaciones(self, torneo_id: str) -> list:
        """
        Deriva recomendaciones del análisis de criterios desbalanceados y
        equipos en bajo rendimiento (RF3-005), sin persistir sugerencias.
        """
        recs: list[str] = []

        for c in self._sug_repo.analizar_criterios(torneo_id):
            desv = c['desv_est']
            if desv > 40:
                recs.append(
                    f"revisar el criterio «{c['criterio_nombre']}», que mostró una "
                    f"dispersión muy alta entre equipos (desviación {desv:.1f})"
                )
            else:
                recs.append(
                    f"redefinir el criterio «{c['criterio_nombre']}», que apenas "
                    f"diferenció a los equipos (desviación {desv:.1f})"
                )

        equipos_bajos = self._sug_repo.analizar_equipos_bajo_rendimiento(torneo_id)
        if equipos_bajos:
            nombres = ", ".join(f"«{e['equipo_nombre']}»" for e in equipos_bajos[:3])
            recs.append(
                f"brindar acompañamiento pedagógico adicional a los equipos de menor "
                f"desempeño ({nombres})"
            )

        return recs
