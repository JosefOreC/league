"""
Implementación concreta del repositorio de Análisis Integral.
Capa: infrastructure/repositories/
Implementa IAnalisisIntegralRepository usando Django ORM + SQL raw con CTEs.

TIEMPO DE RESPUESTA OBJETIVO: < 2 segundos
CACHE CANDIDATE: TTL 60s — considerar caché si el torneo tiene > 100 equipos.

Tablas utilizadas (sin crear nuevas):
    competencia_tournament      — estado, nombre del torneo
    competencia_match           — partidos y rondas
    competencia_match_result    — puntajes por criterio (estado_resultado='DEFINITIVE')
    competencia_criteria        — criterios de evaluación
    competencia_final_ranking   — posición y medalla final
    competencia_team            — nombre y categoría del equipo

NOTA: El campo estado_resultado en la BD usa 'DEFINITIVE' (inglés),
      no 'DEFINITIVO' como en la documentación (que usa terminología de dominio).
"""
from typing import Optional
from django.db import connection

from ...domain.ports.analisis_integral_repository_port import IAnalisisIntegralRepository
from ...domain.entities.analisis_integral import (
    AnalisisIntegral,
    DistribucionCriterio,
    EquipoResumen,
)


class AnalisisIntegralRepositoryImpl(IAnalisisIntegralRepository):
    """
    Repositorio que implementa la lógica de datos para HU-AN-01.
    No contiene reglas de negocio — solo acceso a datos eficiente.
    """

    def torneo_existe(self, torneo_id: str) -> bool:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        return TournamentModel.objects.filter(pk=torneo_id).exists()

    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        try:
            return TournamentModel.objects.values_list("state", flat=True).get(pk=torneo_id)
        except TournamentModel.DoesNotExist:
            return None

    def obtener_analisis(
        self,
        torneo_id: str,
        categoria: Optional[str] = None,
    ) -> Optional[AnalisisIntegral]:
        """
        Query principal: una sola llamada a BD con CTEs.
        Calcula: total_equipos, total_partidos, puntaje_promedio, desviacion_estandar,
                 equipo_max, equipo_min, distribucion_criterio, ranking_final.

        -- INDEX HINT: competencia_match(tournament_id, estado),
        --             competencia_match_result(match_id, estado_resultado),
        --             competencia_final_ranking(tournament_id, posicion_final)
        """
        # Construimos la condición de categoría de forma dinámica
        categoria_filter_eq = ""
        categoria_filter_having = ""
        params_base: list = [torneo_id]

        if categoria:
            categoria_filter_eq = "AND t.category = %s"
            params_base = [torneo_id, categoria]

        sql = f"""
        WITH partidos_torneo AS (
            -- Partidos reales del torneo (excluye BYE)
            SELECT p.id AS partido_id, p.ronda
            FROM competencia_match p
            WHERE p.tournament_id = %s
              AND p.es_bye = FALSE
              AND p.estado = 'FINISHED'
        ),
        resultados_definitivos AS (
            -- Resultados definitivos por equipo y partido
            -- INDEX HINT: competencia_match_result(match_id, estado_resultado)
            SELECT
                mr.id,
                mr.match_id AS partido_id,
                mr.equipo_id,
                mr.criterio_id,
                mr.valor_normalizado AS puntaje,
                t.name AS equipo_nombre,
                t.category AS equipo_categoria
            FROM competencia_match_result mr
            INNER JOIN partidos_torneo pt ON pt.partido_id = mr.match_id
            INNER JOIN competencia_team t ON t.id = mr.equipo_id
            WHERE mr.estado_resultado = 'DEFINITIVE'
              {categoria_filter_eq}
        ),
        puntajes_por_equipo AS (
            -- Puntaje total acumulado por equipo en resultados definitivos
            SELECT
                equipo_id,
                equipo_nombre,
                equipo_categoria,
                SUM(puntaje) AS puntaje_total
            FROM resultados_definitivos
            GROUP BY equipo_id, equipo_nombre, equipo_categoria
        ),
        metricas_globales AS (
            SELECT
                COUNT(DISTINCT equipo_id)                       AS total_equipos,
                COUNT(DISTINCT partido_id)                      AS total_partidos,
                AVG(puntaje)                                    AS puntaje_promedio,
                STDDEV(puntaje)                                 AS desviacion_estandar,
                MAX(puntaje)                                    AS puntaje_maximo,
                MIN(puntaje)                                    AS puntaje_minimo
            FROM resultados_definitivos
        ),
        equipo_max AS (
            SELECT equipo_id, equipo_nombre, puntaje_total
            FROM puntajes_por_equipo
            ORDER BY puntaje_total DESC
            LIMIT 1
        ),
        equipo_min AS (
            SELECT equipo_id, equipo_nombre, puntaje_total
            FROM puntajes_por_equipo
            ORDER BY puntaje_total ASC
            LIMIT 1
        )
        SELECT
            mg.total_equipos,
            mg.total_partidos,
            mg.puntaje_promedio,
            mg.desviacion_estandar,
            mg.puntaje_maximo,
            mg.puntaje_minimo,
            em.equipo_id       AS max_equipo_id,
            em.equipo_nombre   AS max_equipo_nombre,
            em.puntaje_total   AS max_puntaje_total,
            emn.equipo_id      AS min_equipo_id,
            emn.equipo_nombre  AS min_equipo_nombre,
            emn.puntaje_total  AS min_puntaje_total
        FROM metricas_globales mg
        CROSS JOIN equipo_max em
        CROSS JOIN equipo_min emn
        """

        # Ejecutamos la query principal
        params_main = params_base.copy()
        if categoria:
            # El parámetro de torneo_id ya está en params_base[0],
            # el de categoría en params_base[1] si corresponde
            pass

        with connection.cursor() as cursor:
            cursor.execute(sql, params_main)
            row = cursor.fetchone()

        if not row or not row[0]:
            # No hay resultados definitivos
            return None

        (
            total_equipos, total_partidos,
            puntaje_promedio, desviacion_estandar,
            puntaje_maximo, puntaje_minimo,
            max_equipo_id, max_equipo_nombre, max_puntaje_total,
            min_equipo_id, min_equipo_nombre, min_puntaje_total,
        ) = row

        # ── Distribución por criterio ──────────────────────────────────────────
        distribucion = self._obtener_distribucion_criterios(torneo_id, categoria)

        # ── Ranking final con medalla ──────────────────────────────────────────
        ranking = self._obtener_ranking_final(torneo_id, categoria)

        # ── Medallas para equipo_max y equipo_min ─────────────────────────────
        ranking_map = {r["equipo_id"]: r for r in ranking}
        max_info = ranking_map.get(max_equipo_id, {})
        min_info = ranking_map.get(min_equipo_id, {})

        # ── Nombre del torneo ─────────────────────────────────────────────────
        from competencia.infrastructure.adapters.output.models import TournamentModel
        torneo = TournamentModel.objects.values("name").get(pk=torneo_id)

        return AnalisisIntegral(
            torneo_id=torneo_id,
            torneo_nombre=torneo["name"],
            total_equipos=int(total_equipos or 0),
            total_partidos=int(total_partidos or 0),
            puntaje_promedio_global=float(puntaje_promedio or 0),
            desviacion_estandar_global=float(desviacion_estandar or 0),
            puntaje_maximo=float(puntaje_maximo or 0),
            puntaje_minimo=float(puntaje_minimo or 0),
            equipo_max=EquipoResumen(
                equipo_id=max_equipo_id,
                nombre=max_equipo_nombre,
                puntaje_total=float(max_puntaje_total or 0),
                posicion_final=max_info.get("posicion_final"),
                medalla=max_info.get("medalla"),
            ),
            equipo_min=EquipoResumen(
                equipo_id=min_equipo_id,
                nombre=min_equipo_nombre,
                puntaje_total=float(min_puntaje_total or 0),
                posicion_final=min_info.get("posicion_final"),
                medalla=min_info.get("medalla"),
            ),
            distribucion_criterios=distribucion,
            ranking_final=ranking,
            categoria_filtrada=categoria,
        )

    def _obtener_distribucion_criterios(
        self,
        torneo_id: str,
        categoria: Optional[str] = None,
    ) -> list[DistribucionCriterio]:
        """
        Query de distribución de puntajes por criterio.
        -- INDEX HINT: competencia_criteria(tournament_id)
        --             competencia_match_result(criterio_id, estado_resultado)
        """
        categoria_filter = ""
        params: list = [torneo_id]
        if categoria:
            categoria_filter = "AND t.category = %s"
            params.append(categoria)

        sql = f"""
        SELECT
            c.id                    AS criterio_id,
            c.name                  AS criterio_nombre,
            c.value                 AS peso,
            AVG(mr.valor_normalizado) AS promedio,
            MAX(mr.valor_normalizado) AS maximo,
            MIN(mr.valor_normalizado) AS minimo,
            STDDEV(mr.valor_normalizado) AS desviacion_estandar
        FROM competencia_criteria c
        INNER JOIN competencia_match_result mr ON mr.criterio_id = c.id
        INNER JOIN competencia_match p ON p.id = mr.match_id
        INNER JOIN competencia_team t ON t.id = mr.equipo_id
        WHERE c.tournament_id = %s
          AND mr.estado_resultado = 'DEFINITIVE'
          AND p.es_bye = FALSE
          AND p.estado = 'FINISHED'
          {categoria_filter}
        GROUP BY c.id, c.name, c.value
        ORDER BY c.value DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [
            DistribucionCriterio(
                criterio_id=r[0],
                criterio_nombre=r[1],
                peso=float(r[2] or 0),
                promedio=float(r[3] or 0),
                maximo=float(r[4] or 0),
                minimo=float(r[5] or 0),
                desviacion_estandar=float(r[6] or 0),
            )
            for r in rows
        ]

    def _obtener_ranking_final(
        self,
        torneo_id: str,
        categoria: Optional[str] = None,
    ) -> list[dict]:
        """
        Retorna el ranking final del torneo.
        -- INDEX HINT: competencia_final_ranking(tournament_id, posicion_final)
        """
        categoria_filter = ""
        params: list = [torneo_id]
        if categoria:
            categoria_filter = "AND t.category = %s"
            params.append(categoria)

        sql = f"""
        SELECT
            fr.team_id          AS equipo_id,
            t.name              AS equipo_nombre,
            t.category          AS categoria,
            fr.posicion_final,
            fr.puntaje_total_acumulado,
            fr.medalla
        FROM competencia_final_ranking fr
        INNER JOIN competencia_team t ON t.id = fr.team_id
        WHERE fr.tournament_id = %s
          {categoria_filter}
        ORDER BY fr.posicion_final ASC
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [
            {
                "equipo_id": r[0],
                "equipo_nombre": r[1],
                "categoria": r[2],
                "posicion_final": r[3],
                "puntaje_total_acumulado": float(r[4] or 0),
                "medalla": r[5],
            }
            for r in rows
        ]
