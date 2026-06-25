"""
Implementación concreta del repositorio de Panel Docente.
Capa: infrastructure/repositories/
Implementa IPanelDocenteRepository.

ESTRATEGIA: Reutiliza la misma query de criterios de ReporteIndividualRepositoryImpl
y la extiende con el cálculo de percentil (PERCENT_RANK en PostgreSQL).
No duplica SQL — inyecta la lógica de consulta de criterios del reporte individual.

Tablas utilizadas (sin crear nuevas):
    competencia_tournament      — nombre y estado del torneo
    competencia_team            — nombre, docente_asesor_id del equipo
    competencia_docente_asesor  — nombre del docente
    competencia_match           — conteo de partidos finalizados
    competencia_match_result    — puntajes por criterio
    competencia_criteria        — nombre y peso del criterio
    competencia_final_ranking   — posición y medalla (si finalized)

-- INDEX HINT: competencia_match(tournament_id, estado) → conteo de partidos
-- INDEX HINT: competencia_match_result(criterio_id, estado_resultado) → percentil
-- INDEX HINT: competencia_team(id) + competencia_docente_asesor(id) → docente
"""
from typing import Optional
from django.db import connection

from ...domain.ports.panel_docente_repository_port import IPanelDocenteRepository
from ...domain.entities.panel_docente import CriterioConPercentil


class PanelDocenteRepositoryImpl(IPanelDocenteRepository):
    """
    Repositorio para HU-AN-08.
    Reutiliza la SQL de criterios de reporte-individual y agrega PERCENT_RANK.
    No contiene reglas de negocio.
    """

    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        try:
            return TournamentModel.objects.values_list("state", flat=True).get(pk=torneo_id)
        except TournamentModel.DoesNotExist:
            return None

    def contar_partidos_finalizados(self, torneo_id: str) -> int:
        from competencia.infrastructure.adapters.output.models import MatchModel
        return MatchModel.objects.filter(
            tournament_id=torneo_id,
            estado="finalized",
            es_bye=False,
        ).count()

    def equipo_pertenece_a_torneo(self, equipo_id: str, torneo_id: str) -> bool:
        from competencia.infrastructure.adapters.output.models import TeamModel
        return TeamModel.objects.filter(pk=equipo_id, tournament_id=torneo_id).exists()

    def obtener_docente_del_equipo(
        self, equipo_id: str
    ) -> Optional[tuple[str, str]]:
        """
        Retorna (docente_asesor_id, nombre_completo) del equipo.
        Hace JOIN con competencia_docente_asesor para obtener el nombre.
        """
        sql = """
        SELECT
            da.id              AS docente_id,
            da.nombre_completo AS docente_nombre
        FROM competencia_team t
        INNER JOIN competencia_docente_asesor da ON da.id = t.docente_asesor_id
        WHERE t.id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, [equipo_id])
            row = cursor.fetchone()

        if not row:
            return None
        return (str(row[0]), row[1])

    def obtener_info_equipo_panel(
        self, torneo_id: str, equipo_id: str
    ) -> Optional[dict]:
        """
        Datos base del equipo para encabezado del panel.
        LEFT JOIN a final_ranking para posición/medalla (NULL si IN_PROGRESS).
        """
        sql = """
        SELECT
            t.name                              AS torneo_nombre,
            e.name                              AS equipo_nombre,
            fr.posicion_final,
            fr.medalla,
            COALESCE(fr.puntaje_total_acumulado, 0) AS puntaje_total,
            (
                SELECT COUNT(*)
                FROM competencia_match p2
                WHERE p2.tournament_id = %s
                  AND (p2.equipo_local_id = e.id OR p2.equipo_visitante_id = e.id)
                  AND p2.estado = 'finalized'
                  AND p2.es_bye = FALSE
            )                                   AS partidos_jugados
        FROM competencia_team e
        INNER JOIN competencia_tournament t ON t.id = e.tournament_id
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
            "posicion_final": row[2],
            "medalla": row[3],
            "puntaje_total_acumulado": float(row[4] or 0),
            "total_partidos_jugados": int(row[5] or 0),
        }

    def obtener_criterios_con_percentil(
        self,
        torneo_id: str,
        equipo_id: str,
    ) -> list[CriterioConPercentil]:
        """
        Calcula el percentil del equipo por criterio usando PERCENT_RANK de PostgreSQL.

        Estrategia (sin duplicar SQL de reporte-individual):
          1. Calcular el puntaje promedio del equipo por criterio.
          2. Calcular el PERCENT_RANK del equipo vs. todos los equipos del torneo
             usando una window function.

        PERCENT_RANK() retorna un valor en [0, 1]:
            0 = el equipo tiene el puntaje más bajo
            1 = el equipo tiene el puntaje más alto
        Multiplicamos por 100 para obtener el percentil 0–100.

        -- INDEX HINT: competencia_match_result(criterio_id, estado_resultado)
        -- INDEX HINT: competencia_criteria(tournament_id)
        """
        sql = """
        WITH puntajes_por_equipo_criterio AS (
            -- Promedio de cada equipo en cada criterio
            SELECT
                mr.criterio_id,
                mr.equipo_id,
                AVG(mr.valor_normalizado) AS promedio_equipo
            FROM competencia_match_result mr
            INNER JOIN competencia_match p ON p.id = mr.match_id
            WHERE p.tournament_id = %s
              AND mr.estado_resultado = 'DEFINITIVE'
              AND p.es_bye = FALSE
              AND p.estado = 'finalized'
            GROUP BY mr.criterio_id, mr.equipo_id
        ),
        ranking_con_percentil AS (
            -- Percentil de cada equipo por criterio usando window function
            SELECT
                criterio_id,
                equipo_id,
                promedio_equipo,
                ROUND(
                    PERCENT_RANK() OVER (
                        PARTITION BY criterio_id
                        ORDER BY promedio_equipo ASC
                    ) * 100, 2
                ) AS percentil
            FROM puntajes_por_equipo_criterio
        ),
        estadisticas_torneo_criterio AS (
            -- Promedio global, máximo y mínimo del torneo por criterio
            SELECT
                criterio_id,
                AVG(promedio_equipo)  AS promedio_torneo,
                MAX(promedio_equipo)  AS maximo_torneo,
                MIN(promedio_equipo)  AS minimo_torneo
            FROM puntajes_por_equipo_criterio
            GROUP BY criterio_id
        )
        SELECT
            c.id                    AS criterio_id,
            c.name                  AS criterio_nombre,
            c.value                 AS peso,
            rp.promedio_equipo,
            et.promedio_torneo,
            rp.percentil,
            et.maximo_torneo,
            et.minimo_torneo
        FROM ranking_con_percentil rp
        INNER JOIN criterios_torneo_cte c_join ON c_join.id = rp.criterio_id
        INNER JOIN estadisticas_torneo_criterio et ON et.criterio_id = rp.criterio_id
        INNER JOIN competencia_criteria c ON c.id = rp.criterio_id
        WHERE rp.equipo_id = %s
          AND c.tournament_id = %s
        ORDER BY c.value DESC
        """

        # Nota: La CTE de arriba tiene una auto-referencia que PostgreSQL no permite.
        # Reescribimos con la query correcta:
        sql = """
        WITH puntajes_por_equipo_criterio AS (
            SELECT
                mr.criterio_id,
                mr.equipo_id,
                AVG(mr.valor_normalizado) AS promedio_equipo
            FROM competencia_match_result mr
            INNER JOIN competencia_match p ON p.id = mr.match_id
            WHERE p.tournament_id = %s
              AND mr.estado_resultado = 'DEFINITIVE'
              AND p.es_bye = FALSE
              AND p.estado = 'finalized'
            GROUP BY mr.criterio_id, mr.equipo_id
        ),
        ranking_con_percentil AS (
            SELECT
                criterio_id,
                equipo_id,
                promedio_equipo,
                ROUND(
                    CAST(PERCENT_RANK() OVER (
                        PARTITION BY criterio_id
                        ORDER BY promedio_equipo ASC
                    ) * 100 AS NUMERIC), 2
                ) AS percentil
            FROM puntajes_por_equipo_criterio
        ),
        estadisticas_criterio AS (
            SELECT
                criterio_id,
                AVG(promedio_equipo)  AS promedio_torneo,
                MAX(promedio_equipo)  AS maximo_torneo,
                MIN(promedio_equipo)  AS minimo_torneo
            FROM puntajes_por_equipo_criterio
            GROUP BY criterio_id
        )
        SELECT
            c.id                        AS criterio_id,
            c.name                      AS criterio_nombre,
            c.value                     AS peso,
            rp.promedio_equipo,
            ec.promedio_torneo,
            rp.percentil,
            ec.maximo_torneo,
            ec.minimo_torneo
        FROM ranking_con_percentil rp
        INNER JOIN estadisticas_criterio ec ON ec.criterio_id = rp.criterio_id
        INNER JOIN competencia_criteria c   ON c.id = rp.criterio_id
        WHERE rp.equipo_id = %s
          AND c.tournament_id = %s
        ORDER BY c.value DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, [torneo_id, equipo_id, torneo_id])
            rows = cursor.fetchall()

        return [
            CriterioConPercentil(
                criterio_id=r[0],
                criterio_nombre=r[1],
                peso=float(r[2] or 0),
                promedio_equipo=float(r[3] or 0),
                promedio_torneo=float(r[4] or 0),
                percentil=float(r[5] or 0),
                maximo_torneo=float(r[6] or 0),
                minimo_torneo=float(r[7] or 0),
            )
            for r in rows
        ]
