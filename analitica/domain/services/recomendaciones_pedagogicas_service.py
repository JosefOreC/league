"""
Domain Service: RecomendacionesPedagogicasService
Capa: domain/services/
Este servicio contiene lógica de negocio PURA — sin IO, sin imports de
infrastructure/ ni application/.

Regla de negocio (HU-AN-08):
    Dado el percentil del equipo en un criterio:
    - percentil ≤ 25  → TipoRecomendacion.PRACTICA_DIRIGIDA
    - percentil 26–50 → TipoRecomendacion.RECURSO
    - percentil > 50  → TipoRecomendacion.METODOLOGIA

El percentil representa el % de equipos con puntaje menor al del equipo analizado.
Un percentil alto (> 50) significa que el equipo supera a la mayoría → se recomienda
enriquecer con metodologías avanzadas.
Un percentil bajo (≤ 25) significa que el equipo está en el cuartil inferior →
se recomienda práctica dirigida intensiva.
"""
from ..entities.panel_docente import (
    CriterioConPercentil,
    Recomendacion,
    TipoRecomendacion,
)


class RecomendacionesPedagogicasService:
    """
    Servicio de dominio que genera recomendaciones pedagógicas
    basándose en el percentil del equipo por criterio.

    No tiene estado ni dependencias externas — es una función pura
    encapsulada en una clase para inyección de dependencias.
    """

    # ── Contenido de recomendaciones por tipo ──────────────────────────────────
    _DESCRIPCIONES = {
        TipoRecomendacion.PRACTICA_DIRIGIDA: (
            "El equipo se encuentra en el cuartil inferior (percentil ≤ 25) para este criterio. "
            "Se recomienda sesiones de práctica dirigida con supervisión directa para reforzar "
            "las habilidades fundamentales."
        ),
        TipoRecomendacion.RECURSO: (
            "El equipo se ubica en el percentil medio (26–50) para este criterio. "
            "Se recomienda proporcionar recursos de aprendizaje complementarios (guías, "
            "tutoriales, materiales de referencia) para avanzar hacia el cuartil superior."
        ),
        TipoRecomendacion.METODOLOGIA: (
            "El equipo supera a la mayoría de participantes (percentil > 50) en este criterio. "
            "Se recomienda explorar metodologías avanzadas y proyectos de mayor complejidad "
            "para continuar su crecimiento."
        ),
    }

    _ACCIONES = {
        TipoRecomendacion.PRACTICA_DIRIGIDA: [
            "Programar sesiones semanales de práctica supervisada.",
            "Identificar los sub-criterios con menor puntaje y enfocar el entrenamiento.",
            "Asignar ejercicios de refuerzo con retroalimentación inmediata.",
            "Solicitar acompañamiento de un tutor especializado en esta área.",
        ],
        TipoRecomendacion.RECURSO: [
            "Compartir bibliografía y materiales de referencia del criterio.",
            "Proporcionar acceso a plataformas de aprendizaje en línea.",
            "Revisar grabaciones de equipos con alto desempeño en este criterio.",
            "Organizar una sesión de intercambio de experiencias con equipos del cuartil superior.",
        ],
        TipoRecomendacion.METODOLOGIA: [
            "Proponer retos de mayor complejidad y autonomía.",
            "Conectar al equipo con comunidades de práctica avanzada.",
            "Diseñar un proyecto de investigación aplicada sobre este criterio.",
            "Explorar certificaciones o competencias de nivel avanzado en esta área.",
        ],
    }

    def generar_recomendaciones(
        self,
        criterios: list[CriterioConPercentil],
    ) -> list[Recomendacion]:
        """
        Genera una lista de recomendaciones pedagógicas para cada criterio.

        Args:
            criterios: Lista de criterios con su percentil calculado.

        Returns:
            Lista de Recomendacion ordenada de menor a mayor percentil
            (las áreas de mejora urgente primero).
        """
        recomendaciones: list[Recomendacion] = []

        for criterio in criterios:
            tipo = self._clasificar_por_percentil(criterio.percentil)
            recomendaciones.append(
                Recomendacion(
                    criterio_id=criterio.criterio_id,
                    criterio_nombre=criterio.criterio_nombre,
                    tipo=tipo,
                    percentil=criterio.percentil,
                    descripcion=self._DESCRIPCIONES[tipo],
                    acciones_sugeridas=self._ACCIONES[tipo],
                )
            )

        # Ordenar: áreas críticas primero (menor percentil → mayor prioridad)
        recomendaciones.sort(key=lambda r: r.percentil)
        return recomendaciones

    @staticmethod
    def _clasificar_por_percentil(percentil: float) -> TipoRecomendacion:
        """
        Regla de negocio central de HU-AN-08:
            percentil ≤ 25  → PRACTICA_DIRIGIDA
            percentil 26–50 → RECURSO
            percentil > 50  → METODOLOGIA
        """
        if percentil <= 25.0:
            return TipoRecomendacion.PRACTICA_DIRIGIDA
        elif percentil <= 50.0:
            return TipoRecomendacion.RECURSO
        else:
            return TipoRecomendacion.METODOLOGIA
