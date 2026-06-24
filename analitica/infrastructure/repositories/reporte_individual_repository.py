"""
Implementación concreta del repositorio de Reporte Individual.
Capa: infrastructure/repositories/
Implementa IReporteIndividualRepository usando Django ORM + SQL raw.

Tablas utilizadas (sin crear nuevas):
    competencia_tournament      — estado y nombre del torneo
    competencia_team            — nombre, categoría, representante, docente_asesor
    competencia_institution     — nombre de institución
    competencia_match           — partidos del equipo con ronda y rival
    competencia_match_result    — puntajes por criterio (estado_resultado='DEFINITIVE')
    competencia_criteria        — nombre y peso del criterio
    competencia_final_ranking   — posición y medalla final

-- INDEX HINT para queries de este repositorio:
--   competencia_match_result(equipo_id, estado_resultado)       → HU-AN-02
--   competencia_match(tournament_id, estado)                    → filtro partidos
--   competencia_final_ranking(tournament_id, team_id)          → posición del equipo
"""
from typing import Optional
from django.db import connection

from ...domain.ports.reporte_individual_repository_port import IReporteIndividualRepository
from ...domain.entities.reporte_individual import (
    ReporteIndividual,
    ResultadoPartido,
    DetalleCriterio,
    EvolucionRonda,
)


class ReporteIndividualRepositoryImpl(IReporteIndividualRepository):
    """
    Repositorio que implementa la lógica de datos para HU-AN-02.
    No contiene reglas de negocio — solo acceso a datos eficiente.
    """

    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        try:
            return TournamentModel.objects.values_list("state", flat=True).get(pk=torneo_id)
        except TournamentModel.DoesNotExist:
            return None

    def equipo_pertenece_a_torneo(self, equipo_id: str, torneo_id: str) -> bool:
        from competencia.infrastructure.adapters.output.models import TeamModel
        return TeamModel.objects.filter(pk=equipo_id, tournament_id=torneo_id).exists()

    def obtener_representante_y_docente(
        self, equipo_id: str
    ) -> Optional[tuple[str, str]]:
        from competencia.infrastructure.adapters.output.models import TeamModel
        try:
            team = TeamModel.objects.values(
                "representante_id", "docente_asesor_id"
            ).get(pk=equipo_id)
            return (team["representante_id"], str(team["docente_asesor_id"]))
        except TeamModel.DoesNotExist:
            return None

    def obtener_reporte(
        self,
        torneo_id: str,
        equipo_id: str,
    ) -> Optional[ReporteIndividual]:
        """
        Obtiene el reporte completo del equipo en el torneo.
        Usa 4 queries SQL eficientes (sin N+1):
          1. Datos del equipo e institución
          2. Partidos del equipo con puntajes
          3. Detalle por criterio (avg/max/min equipo vs. promedio torneo)
          4. Evolución por ronda
        Todos comparten la misma condición de filtro.
        """
        # ── 1. Datos base del equipo ───────────────────────────────────────────
        equipo_info = self._obtener_info_equipo(torneo_id, equipo_id)
        if equipo_info is None:
            return None

        # ── 2. Partidos del equipo ─────────────────────────────────────────────
        partidos = self._obtener_partidos(torneo_id, equipo_id)
        if not partidos:
            return None  # Sin resultados DEFINITIVO

        # ── 3. Detalle por criterio ────────────────────────────────────────────
        criterios = self._obtener_detalle_criterios(torneo_id, equipo_id)

        # ── 4. Evolución por ronda ─────────────────────────────────────────────
        evolucion = self._obtener_evolucion_por_ronda(torneo_id, equipo_id)

        # ── Métricas derivadas ─────────────────────────────────────────────────
        total_jugados = len(partidos)
        victorias = sum(1 for p in partidos if p.es_victoria)
        derrotas = total_jugados - victorias

        puntaje_total = sum(p.puntaje_equipo for p in partidos)
        prom_torneo = equipo_info["promedio_torneo"]
        comparativa = (
            ((puntaje_total - prom_torneo) / prom_torneo * 100)
            if prom_torneo else 0.0
        )

        return ReporteIndividual(
            torneo_id=torneo_id,
            torneo_nombre=equipo_info["torneo_nombre"],
            equipo_id=equipo_id,
            equipo_nombre=equipo_info["equipo_nombre"],
            categoria=equipo_info["categoria"],
            institucion_nombre=equipo_info["institucion_nombre"],
            posicion_final=equipo_info["posicion_final"],
            medalla=equipo_info["medalla"],
            puntaje_total_acumulado=round(puntaje_total, 4),
            promedio_puntaje_torneo=round(prom_torneo, 4),
            comparativa_vs_promedio_torneo=round(comparativa, 2),
            partidos=partidos,
            detalle_criterios=criterios,
            evolucion_por_ronda=evolucion,
            total_partidos_jugados=total_jugados,
            victorias=victorias,
            derrotas=derrotas,
        )

    def _obtener_info_equipo(self, torneo_id: str, equipo_id: str) -> Optional[dict]:
        """
        Datos base del equipo, institución, torneo, ranking y promedio global del torneo.
        Single query con LEFT JOIN a final_ranking.
        """
        sql = """
        SELECT
            t.name                              AS torneo_nombre,
            e.name                              AS equipo_nombre,
            e.category                          AS categoria,
            i.name                              AS institucion_nombre,
            fr.posicion_final,
            fr.medalla,
            (
                SELECT AVG(mr2.valor_normalizado)
                FROM competencia_match_result mr2
                INNER JOIN competencia_match p2 ON p2.id = mr2.match_id
                WHERE p2.tournament_id = %s
                  AND mr2.estado_resultado = 'DEFINITIVE'
                  AND p2.es_bye = FALSE
                  AND p2.estado = 'FINISHED'
            )                                   AS promedio_torneo
        FROM competencia_team e
        INNER JOIN competencia_tournament t ON t.id = e.tournament_id
        INNER JOIN competencia_institution i ON i.id = e.institution_id
        LEFT JOIN competencia_final_ranking fr
               ON fr.team_id = e.id AND fr.tournament_id = %s
        WHERE e.id = %s
          AND e.tournament_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, [torneo_id, torneo_id, equipo_id, torneo_id])
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "torneo_nombre": row[0],
            "equipo_nombre": row[1],
            "categoria": row[2],
            "institucion_nombre": row[3],
            "posicion_final": row[4],
            "medalla": row[5],
            "promedio_torneo": float(row[6] or 0),
        }

    def _obtener_partidos(
        self, torneo_id: str, equipo_id: str
    ) -> list[ResultadoPartido]:
        """
        Todos los partidos del equipo con: rival, puntajes, ganador.
        Usa un LEFT JOIN para obtener puntaje del rival en el mismo partido.

        -- INDEX HINT: competencia_match_result(equipo_id, estado_resultado)
        --             competencia_match(tournament_id, estado)
        """
        sql = """
        WITH puntajes_partido AS (
            -- Puntaje total de cada equipo por partido (sumando todos los criterios)
            SELECT
                mr.match_id,
                mr.equipo_id,
                SUM(mr.valor_normalizado) AS puntaje_total
            FROM competencia_match_result mr
            INNER JOIN competencia_match p ON p.id = mr.match_id
            WHERE p.tournament_id = %s
              AND mr.estado_resultado = 'DEFINITIVE'
              AND p.es_bye = FALSE
              AND p.estado = 'FINISHED'
            GROUP BY mr.match_id, mr.equipo_id
        )
        SELECT
            p.id                        AS partido_id,
            p.ronda,
            -- Rival: el otro equipo del partido
            CASE
                WHEN p.equipo_local_id = %s THEN p.equipo_visitante_id
                ELSE p.equipo_local_id
            END                         AS rival_id,
            CASE
                WHEN p.equipo_local_id = %s THEN ev.name
                ELSE el.name
            END                         AS rival_nombre,
            mi.puntaje_total            AS puntaje_equipo,
            COALESCE(mr2.puntaje_total, 0) AS puntaje_rival,
            p.ganador_id,
            p.fecha_programada
        FROM competencia_match p
        INNER JOIN competencia_team el ON el.id = p.equipo_local_id
        LEFT  JOIN competencia_team ev ON ev.id = p.equipo_visitante_id
        INNER JOIN puntajes_partido mi
               ON mi.match_id = p.id AND mi.equipo_id = %s
        LEFT  JOIN puntajes_partido mr2
               ON mr2.match_id = p.id AND mr2.equipo_id != %s
        WHERE p.tournament_id = %s
          AND (p.equipo_local_id = %s OR p.equipo_visitante_id = %s)
          AND p.es_bye = FALSE
          AND p.estado = 'FINISHED'
        ORDER BY p.ronda ASC
        """
        params = [
            torneo_id,
            equipo_id, equipo_id,  # CASE rival_id
            equipo_id, equipo_id,  # JOIN puntajes mi y mr2
            torneo_id, equipo_id, equipo_id,
        ]

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [
            ResultadoPartido(
                partido_id=r[0],
                ronda=r[1],
                rival_id=r[2] or "",
                rival_nombre=r[3] or "BYE",
                puntaje_equipo=float(r[4] or 0),
                puntaje_rival=float(r[5] or 0),
                ganador_id=r[6],
                es_victoria=(r[6] == equipo_id),
                fecha_programada=r[7].isoformat() if r[7] else None,
            )
            for r in rows
        ]

    def _obtener_detalle_criterios(
        self, torneo_id: str, equipo_id: str
    ) -> list[DetalleCriterio]:
        """
        Estadísticas por criterio: promedio/max/min del equipo vs. promedio global del torneo.
        Query única con subquery correlacionada para el promedio del torneo.

        -- INDEX HINT: competencia_match_result(criterio_id, estado_resultado)
        --             competencia_criteria(tournament_id)
        """
        sql = """
        SELECT
            c.id                            AS criterio_id,
            c.name                          AS criterio_nombre,
            c.value                         AS peso,
            AVG(mr.valor_normalizado)       AS promedio_equipo,
            MAX(mr.valor_normalizado)       AS maximo_equipo,
            MIN(mr.valor_normalizado)       AS minimo_equipo,
            (
                SELECT AVG(mr2.valor_normalizado)
                FROM competencia_match_result mr2
                INNER JOIN competencia_match p2 ON p2.id = mr2.match_id
                WHERE mr2.criterio_id = c.id
                  AND p2.tournament_id = %s
                  AND mr2.estado_resultado = 'DEFINITIVE'
                  AND p2.es_bye = FALSE
                  AND p2.estado = 'FINISHED'
            )                               AS promedio_torneo
        FROM competencia_criteria c
        INNER JOIN competencia_match_result mr ON mr.criterio_id = c.id
        INNER JOIN competencia_match p ON p.id = mr.match_id
        WHERE mr.equipo_id = %s
          AND c.tournament_id = %s
          AND mr.estado_resultado = 'DEFINITIVE'
          AND p.es_bye = FALSE
          AND p.estado = 'FINISHED'
          AND p.tournament_id = %s
        GROUP BY c.id, c.name, c.value
        ORDER BY c.value DESC
        """
        params = [torneo_id, equipo_id, torneo_id, torneo_id]

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        result = []
        for r in rows:
            prom_equipo = float(r[3] or 0)
            prom_torneo = float(r[6] or 0)
            comparativa = (
                ((prom_equipo - prom_torneo) / prom_torneo * 100)
                if prom_torneo else 0.0
            )
            result.append(DetalleCriterio(
                criterio_id=r[0],
                criterio_nombre=r[1],
                peso=float(r[2] or 0),
                promedio_equipo=round(prom_equipo, 4),
                maximo_equipo=float(r[4] or 0),
                minimo_equipo=float(r[5] or 0),
                promedio_torneo=round(prom_torneo, 4),
                comparativa_vs_promedio=round(comparativa, 2),
            ))
        return result

    def _obtener_evolucion_por_ronda(
        self, torneo_id: str, equipo_id: str
    ) -> list[EvolucionRonda]:
        """
        Puntaje del equipo agrupado por ronda, con acumulado progresivo.
        """
        sql = """
        SELECT
            p.ronda,
            SUM(mr.valor_normalizado) AS puntaje_ronda
        FROM competencia_match_result mr
        INNER JOIN competencia_match p ON p.id = mr.match_id
        WHERE mr.equipo_id = %s
          AND p.tournament_id = %s
          AND mr.estado_resultado = 'DEFINITIVE'
          AND p.es_bye = FALSE
          AND p.estado = 'FINISHED'
        GROUP BY p.ronda
        ORDER BY p.ronda ASC
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, [equipo_id, torneo_id])
            rows = cursor.fetchall()

        evolucion = []
        acumulado = 0.0
        for r in rows:
            ronda_puntaje = float(r[1] or 0)
            acumulado += ronda_puntaje
            evolucion.append(EvolucionRonda(
                ronda=r[0],
                puntaje_ronda=round(ronda_puntaje, 4),
                puntaje_acumulado=round(acumulado, 4),
            ))
        return evolucion
