from typing import Optional
from django.db import connection
from django.db.models import Max

from ...domain.ports.resumen_ejecutivo_repository_port import IResumenEjecutivoRepository
from ...domain.entities.resumen_ejecutivo import (
    ResumenEjecutivo,
    MetricasResumen,
    EquipoPodio,
)
from ..adapters.output.models import ResumenEjecutivoModel


class ResumenEjecutivoRepositoryImpl(IResumenEjecutivoRepository):

    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        try:
            return TournamentModel.objects.values_list("state", flat=True).get(pk=torneo_id)
        except TournamentModel.DoesNotExist:
            return None

    def existen_resultados_definitivos(self, torneo_id: str) -> bool:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT EXISTS (
                    SELECT 1
                    FROM competencia_match_result mr
                    INNER JOIN competencia_match m ON m.id = mr.match_id
                    WHERE m.tournament_id = %s
                      AND mr.estado_resultado = 'DEFINITIVE'
                )
            ''', [torneo_id])
            return bool(cursor.fetchone()[0])

    def obtener_metricas(self, torneo_id: str) -> Optional[MetricasResumen]:
        # ── Datos del torneo + totales (una query con subconsultas) ─────────
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    t.name        AS torneo_nombre,
                    t.date_start,
                    t.date_end,
                    (
                        SELECT COUNT(*) FROM competencia_team eq
                        WHERE eq.tournament_id = t.id
                          AND eq.estado_inscripcion = 'APROBADO'
                    ) AS total_equipos,
                    (
                        SELECT COUNT(DISTINCT eq.institution_id) FROM competencia_team eq
                        WHERE eq.tournament_id = t.id
                          AND eq.estado_inscripcion = 'APROBADO'
                    ) AS total_instituciones,
                    (
                        SELECT COUNT(*)
                        FROM competencia_participant p
                        INNER JOIN competencia_team eq ON eq.id = p.team_id
                        WHERE eq.tournament_id = t.id
                          AND eq.estado_inscripcion = 'APROBADO'
                    ) AS total_participantes
                FROM competencia_tournament t
                WHERE t.id = %s
            ''', [torneo_id])
            cols = [c[0] for c in cursor.description]
            fila = cursor.fetchone()

        if not fila:
            return None
        base = dict(zip(cols, fila))

        # ── Sede: ciudad más frecuente entre las instituciones participantes ─
        sede = self._obtener_sede(torneo_id)

        # ── Podio (top 3 de final_ranking) ──────────────────────────────────
        podio = self._obtener_podio(torneo_id)

        # ── Criterio determinante + promedio global + nivel de competencia ──
        criterio_det, prom_global, nivel = self._obtener_analisis(torneo_id)

        return MetricasResumen(
            torneo_nombre=base['torneo_nombre'],
            fecha_inicio=base['date_start'].isoformat() if base['date_start'] else '',
            fecha_fin=base['date_end'].isoformat() if base['date_end'] else '',
            sede=sede,
            total_equipos=base['total_equipos'] or 0,
            total_instituciones=base['total_instituciones'] or 0,
            total_participantes=base['total_participantes'] or 0,
            podio=podio,
            criterio_determinante=criterio_det,
            puntaje_promedio_global=prom_global,
            nivel_competencia=nivel,
            recomendaciones=[],
        )

    def _obtener_sede(self, torneo_id: str) -> str:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT i.city, COUNT(*) AS n
                FROM competencia_team eq
                INNER JOIN competencia_institution i ON i.id = eq.institution_id
                WHERE eq.tournament_id = %s
                  AND eq.estado_inscripcion = 'APROBADO'
                GROUP BY i.city
                ORDER BY n DESC
                LIMIT 1
            ''', [torneo_id])
            row = cursor.fetchone()
        return row[0] if row and row[0] else 'sede por confirmar'

    def _obtener_podio(self, torneo_id: str) -> list:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    fr.team_id,
                    eq.name              AS equipo_nombre,
                    i.name               AS institucion_nombre,
                    fr.posicion_final,
                    fr.puntaje_total_acumulado,
                    COALESCE(fr.medalla, '') AS medalla
                FROM competencia_final_ranking fr
                INNER JOIN competencia_team eq ON eq.id = fr.team_id
                INNER JOIN competencia_institution i ON i.id = eq.institution_id
                WHERE fr.tournament_id = %s
                ORDER BY fr.posicion_final ASC
                LIMIT 3
            ''', [torneo_id])
            cols  = [c[0] for c in cursor.description]
            filas = [dict(zip(cols, row)) for row in cursor.fetchall()]

        return [
            EquipoPodio(
                equipo_id=f['team_id'],
                nombre=f['equipo_nombre'],
                institucion=f['institucion_nombre'],
                posicion_final=f['posicion_final'],
                puntaje=float(f['puntaje_total_acumulado'] or 0),
                medalla=f['medalla'],
            )
            for f in filas
        ]

    def _obtener_analisis(self, torneo_id: str) -> tuple:
        """
        Retorna (criterio_determinante, promedio_global, nivel_competencia).
        - criterio determinante = criterio con mayor peso (value).
        - nivel = clasificación según STDDEV del puntaje final entre equipos.
        """
        with connection.cursor() as cursor:
            # Criterio de mayor peso
            cursor.execute('''
                SELECT name
                FROM competencia_criteria
                WHERE tournament_id = %s
                ORDER BY value DESC
                LIMIT 1
            ''', [torneo_id])
            row = cursor.fetchone()
            criterio_det = row[0] if row else ''

            # Promedio global + desviación del puntaje final
            cursor.execute('''
                SELECT
                    COALESCE(AVG(puntaje_total_acumulado), 0)    AS prom,
                    COALESCE(STDDEV(puntaje_total_acumulado), 0) AS desv
                FROM competencia_final_ranking
                WHERE tournament_id = %s
            ''', [torneo_id])
            prom, desv = cursor.fetchone()

        prom_global = round(float(prom), 2)
        desv = float(desv)
        if desv > 20:
            nivel = 'ALTO'
        elif desv < 5:
            nivel = 'HOMOGENEO'
        else:
            nivel = 'MEDIO'

        return criterio_det, prom_global, nivel

    def siguiente_version(self, torneo_id: str) -> int:
        actual = ResumenEjecutivoModel.objects.filter(
            torneo_id=torneo_id
        ).aggregate(m=Max('version'))['m']
        return (actual or 0) + 1

    def guardar(
        self,
        torneo_id: str,
        resumen_texto: str,
        tono: str,
        version: int,
        metricas_usadas: dict,
    ) -> ResumenEjecutivo:
        obj = ResumenEjecutivoModel.objects.create(
            torneo_id=torneo_id,
            resumen_texto=resumen_texto,
            tono=tono,
            version=version,
            metricas_usadas=metricas_usadas,
        )
        return ResumenEjecutivo(
            id=str(obj.id),
            torneo_id=obj.torneo_id,
            resumen_texto=obj.resumen_texto,
            tono=obj.tono,
            version=obj.version,
            metricas_usadas=obj.metricas_usadas,
            generado_en=obj.generado_en.isoformat() if obj.generado_en else '',
        )
