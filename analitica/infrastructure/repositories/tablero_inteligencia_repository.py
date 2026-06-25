"""
Implementación concreta del repositorio de Tablero de Inteligencia.
Capa: infrastructure/repositories/
Implementa ITableroInteligenciaRepository usando SQL raw con máximo 2 queries.

TIEMPO DE RESPUESTA OBJETIVO: < 1 segundo
CACHE CANDIDATE: TTL 30s — este endpoint puede ser consultado frecuentemente
                 durante el torneo en vivo.

Tablas utilizadas (sin crear nuevas):
    competencia_tournament      — nombre y estado del torneo
    competencia_match           — estado de partidos, fecha_programada
    competencia_team            — nombre de equipos
    competencia_match_result    — puntajes acumulados
    competencia_final_ranking   — posición y medalla (si finalized)
    competencia_standing        — posición actual durante IN_PROGRESS

Índices críticos para rendimiento < 1s:
-- INDEX HINT: competencia_match(tournament_id, estado)               → filtro partidos
-- INDEX HINT: competencia_match(fecha_programada, estado)            → alertas retraso
--             WHERE estado = 'PENDING' (índice parcial en ARQUITECTURA_ANALITICA)
-- INDEX HINT: competencia_match_result(match_id)                    → puntajes
"""
from typing import Optional
from datetime import datetime, timezone
from django.db import connection

from ...domain.ports.tablero_inteligencia_repository_port import ITableroInteligenciaRepository
from ...domain.entities.tablero_inteligencia import (
    TableroInteligencia,
    AlertaActiva,
    EstadoEquipoTablero,
    PartidoEnCurso,
    SeveridadAlerta,
    TipoAlerta,
)

# Umbral en minutos para considerar un partido como "retrasado"
MINUTOS_RETRASO_ALERTA = 30


class TableroInteligenciaRepositoryImpl(ITableroInteligenciaRepository):
    """
    Repositorio que implementa la lógica de datos para HU-AN-04.
    Máximo 2 queries a la BD. No contiene reglas de negocio.
    """

    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        try:
            return TournamentModel.objects.values_list("state", flat=True).get(pk=torneo_id)
        except TournamentModel.DoesNotExist:
            return None

    def obtener_tablero(self, torneo_id: str) -> Optional[TableroInteligencia]:
        """
        Construye el tablero completo en máximo 2 roundtrips:
            Query 1 — Métricas globales + top 3 + partidos en curso
            Query 2 — Alertas: partidos retrasados + equipos sin resultados
        """
        # ── Query 1: Métricas, top-3 y partidos próximos ─────────────────────
        metricas = self._query_metricas_y_top3(torneo_id)
        if metricas is None:
            return None

        # ── Query 2: Alertas activas ───────────────────────────────────────────
        alertas = self._query_alertas(torneo_id, metricas["estado_torneo"])

        return TableroInteligencia(
            torneo_id=torneo_id,
            torneo_nombre=metricas["torneo_nombre"],
            estado_torneo=metricas["estado_torneo"],
            total_equipos=metricas["total_equipos"],
            total_partidos=metricas["total_partidos"],
            partidos_finalizados=metricas["partidos_finalizados"],
            partidos_pendientes=metricas["partidos_pendientes"],
            partidos_en_progreso=metricas["partidos_en_progreso"],
            porcentaje_avance=metricas["porcentaje_avance"],
            top_3=metricas["top_3"],
            partidos_proximos=metricas["partidos_proximos"],
            alertas_activas=alertas,
        )

    def _query_metricas_y_top3(self, torneo_id: str) -> Optional[dict]:
        """
        Query 1: Una sola llamada que obtiene métricas del torneo, top-3 y partidos
        pendientes/en-progreso.

        -- INDEX HINT: competencia_match(tournament_id, estado)
        -- INDEX HINT: competencia_standing(tournament_id, posicion)
        -- INDEX HINT: competencia_final_ranking(tournament_id, posicion_final)
        """
        # ── 1a. Datos base del torneo y contadores de partidos ────────────────
        sql_metricas = """
        SELECT
            t.name                                              AS torneo_nombre,
            t.state                                             AS estado_torneo,
            COUNT(DISTINCT e.id)                                AS total_equipos,
            COUNT(DISTINCT p.id)                                AS total_partidos,
            COUNT(DISTINCT p.id) FILTER (WHERE p.estado = 'finalized')   AS partidos_finalizados,
            COUNT(DISTINCT p.id) FILTER (WHERE p.estado = 'PENDING')    AS partidos_pendientes,
            COUNT(DISTINCT p.id) FILTER (WHERE p.estado = 'IN_PROGRESS') AS partidos_en_progreso
        FROM competencia_tournament t
        LEFT JOIN competencia_team e    ON e.tournament_id = t.id
        LEFT JOIN competencia_match p   ON p.tournament_id = t.id AND p.es_bye = FALSE
        WHERE t.id = %s
        GROUP BY t.id, t.name, t.state
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_metricas, [torneo_id])
            row = cursor.fetchone()

        if not row:
            return None

        torneo_nombre, estado_torneo, total_equipos, total_partidos, \
            partidos_finalizados, partidos_pendientes, partidos_en_progreso = row

        total_partidos = int(total_partidos or 0)
        partidos_finalizados = int(partidos_finalizados or 0)
        porcentaje_avance = (
            round(partidos_finalizados / total_partidos * 100, 1)
            if total_partidos > 0 else 0.0
        )

        # ── 1b. Top 3: desde ranking_final (finalized) o standings (IN_PROGRESS) ──
        top_3 = self._obtener_top3(torneo_id, estado_torneo)

        # ── 1c. Partidos próximos (PENDING + IN_PROGRESS, límite 10) ─────────
        partidos_proximos = self._obtener_partidos_proximos(torneo_id)

        return {
            "torneo_nombre": torneo_nombre,
            "estado_torneo": estado_torneo,
            "total_equipos": int(total_equipos or 0),
            "total_partidos": total_partidos,
            "partidos_finalizados": partidos_finalizados,
            "partidos_pendientes": int(partidos_pendientes or 0),
            "partidos_en_progreso": int(partidos_en_progreso or 0),
            "porcentaje_avance": porcentaje_avance,
            "top_3": top_3,
            "partidos_proximos": partidos_proximos,
        }

    def _obtener_top3(
        self, torneo_id: str, estado_torneo: str
    ) -> list[EstadoEquipoTablero]:
        """
        Top 3 desde ranking_final si finalized, desde standings si IN_PROGRESS.
        Partidos jugados y victorias se calculan desde competencia_match.
        """
        if estado_torneo == "finalized":
            sql = """
            SELECT
                e.id, e.name,
                fr.posicion_final,
                fr.puntaje_total_acumulado,
                fr.medalla,
                COUNT(DISTINCT p.id) FILTER (WHERE p.estado = 'finalized')  AS partidos_jugados,
                COUNT(DISTINCT p.id) FILTER (WHERE p.estado = 'finalized'
                    AND p.ganador_id = e.id)                                AS victorias
            FROM competencia_final_ranking fr
            INNER JOIN competencia_team e ON e.id = fr.team_id
            LEFT JOIN competencia_match p ON p.tournament_id = %s
                AND (p.equipo_local_id = e.id OR p.equipo_visitante_id = e.id)
                AND p.es_bye = FALSE
            WHERE fr.tournament_id = %s
            GROUP BY e.id, e.name, fr.posicion_final, fr.puntaje_total_acumulado, fr.medalla
            ORDER BY fr.posicion_final ASC
            LIMIT 3
            """
            params = [torneo_id, torneo_id]
        else:
            # IN_PROGRESS: usar standings para posición provisional
            sql = """
            SELECT
                e.id, e.name,
                s.posicion,
                s.puntaje_favor,
                NULL AS medalla,
                s.partidos_jugados,
                s.victorias
            FROM competencia_standing s
            INNER JOIN competencia_team e ON e.id = s.team_id
            WHERE s.tournament_id = %s
              AND s.posicion > 0
            ORDER BY s.posicion ASC
            LIMIT 3
            """
            params = [torneo_id]

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [
            EstadoEquipoTablero(
                equipo_id=r[0],
                equipo_nombre=r[1],
                posicion_actual=r[2] or 0,
                puntaje_acumulado=float(r[3] or 0),
                medalla=r[4],
                partidos_jugados=int(r[5] or 0),
                victorias=int(r[6] or 0),
            )
            for r in rows
        ]

    def _obtener_partidos_proximos(self, torneo_id: str) -> list[PartidoEnCurso]:
        """
        Partidos PENDING o IN_PROGRESS ordenados por fecha_programada.
        Limitado a 10 para no saturar la respuesta.
        """
        now = datetime.now(timezone.utc)

        sql = """
        SELECT
            p.id, p.ronda,
            p.equipo_local_id,  el.name AS equipo_local_nombre,
            p.equipo_visitante_id, ev.name AS equipo_visitante_nombre,
            p.estado, p.fecha_programada
        FROM competencia_match p
        LEFT JOIN competencia_team el ON el.id = p.equipo_local_id
        LEFT JOIN competencia_team ev ON ev.id = p.equipo_visitante_id
        WHERE p.tournament_id = %s
          AND p.estado IN ('PENDING', 'IN_PROGRESS')
          AND p.es_bye = FALSE
        ORDER BY
            CASE WHEN p.estado = 'IN_PROGRESS' THEN 0 ELSE 1 END,
            p.fecha_programada ASC NULLS LAST
        LIMIT 10
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, [torneo_id])
            rows = cursor.fetchall()

        partidos = []
        for r in rows:
            fecha_prog = r[7]
            minutos_retraso = None
            if fecha_prog and r[6] == "PENDING":
                # Calcular retraso si la fecha ya pasó
                # Asegurar que fecha_prog sea aware
                if fecha_prog.tzinfo is None:
                    fecha_prog = fecha_prog.replace(tzinfo=timezone.utc)
                delta = (now - fecha_prog).total_seconds() / 60
                if delta > 0:
                    minutos_retraso = int(delta)

            partidos.append(PartidoEnCurso(
                partido_id=r[0],
                ronda=r[1],
                equipo_local_id=r[2] or "",
                equipo_local_nombre=r[3] or "TBD",
                equipo_visitante_id=r[4],
                equipo_visitante_nombre=r[5] or "TBD",
                estado=r[6],
                fecha_programada=r[7].isoformat() if r[7] else None,
                minutos_retraso=minutos_retraso,
            ))
        return partidos

    def _query_alertas(
        self, torneo_id: str, estado_torneo: str
    ) -> list[AlertaActiva]:
        """
        Query 2: Genera alertas activas.

        Tipos de alerta detectados:
          - PARTIDO_RETRASADO: partido PENDING con fecha_programada vencida > 30 min
          - CAMBIO_TOP3: equipos que tienen puntaje para entrar al top 3 pero
                         no están en el ranking actual (aproximación práctica)
          - SIN_RESULTADOS: equipos con partidos finalized sin ningún resultado registrado

        -- INDEX HINT: competencia_match(fecha_programada, estado) WHERE estado='PENDING'
        -- INDEX HINT: competencia_match_result(match_id)
        """
        alertas: list[AlertaActiva] = []
        now = datetime.now(timezone.utc)

        # ── Alerta 1: Partidos retrasados ──────────────────────────────────────
        sql_retrasados = """
        SELECT
            p.id AS partido_id,
            p.fecha_programada,
            el.name AS equipo_local,
            ev.name AS equipo_visitante
        FROM competencia_match p
        LEFT JOIN competencia_team el ON el.id = p.equipo_local_id
        LEFT JOIN competencia_team ev ON ev.id = p.equipo_visitante_id
        WHERE p.tournament_id = %s
          AND p.estado = 'PENDING'
          AND p.es_bye = FALSE
          AND p.fecha_programada IS NOT NULL
          AND p.fecha_programada < %s - INTERVAL '30 minutes'
        ORDER BY p.fecha_programada ASC
        LIMIT 20
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_retrasados, [torneo_id, now])
            retrasados = cursor.fetchall()

        for r in retrasados:
            fecha_prog = r[1]
            if fecha_prog.tzinfo is None:
                fecha_prog = fecha_prog.replace(tzinfo=timezone.utc)
            minutos = int((now - fecha_prog).total_seconds() / 60)
            alertas.append(AlertaActiva(
                tipo=TipoAlerta.PARTIDO_RETRASADO,
                severidad=SeveridadAlerta.ADVERTENCIA if minutos < 60 else SeveridadAlerta.ERROR,
                mensaje=(
                    f"Partido entre '{r[2]}' y '{r[3]}' está retrasado "
                    f"{minutos} min (programado: {r[1].strftime('%H:%M')})."
                ),
                entidad_ref_id=r[0],
                minutos_retraso=minutos,
            ))

        # ── Alerta 2: Partidos finalizados sin resultados registrados ──────────
        sql_sin_resultados = """
        SELECT
            p.id AS partido_id,
            el.name AS equipo_local,
            ev.name AS equipo_visitante,
            p.ronda
        FROM competencia_match p
        LEFT JOIN competencia_team el ON el.id = p.equipo_local_id
        LEFT JOIN competencia_team ev ON ev.id = p.equipo_visitante_id
        WHERE p.tournament_id = %s
          AND p.estado = 'finalized'
          AND p.es_bye = FALSE
          AND NOT EXISTS (
              SELECT 1 FROM competencia_match_result mr
              WHERE mr.match_id = p.id
          )
        ORDER BY p.ronda ASC
        LIMIT 10
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_sin_resultados, [torneo_id])
            sin_resultados = cursor.fetchall()

        for r in sin_resultados:
            alertas.append(AlertaActiva(
                tipo=TipoAlerta.SIN_RESULTADOS,
                severidad=SeveridadAlerta.ADVERTENCIA,
                mensaje=(
                    f"Partido (ronda {r[3]}) entre '{r[1]}' y '{r[2]}' "
                    f"está finalized pero no tiene resultados registrados."
                ),
                entidad_ref_id=r[0],
            ))

        return alertas
