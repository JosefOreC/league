from typing import Optional
from django.db import connection

from ...domain.ports.reporte_institucional_repository_port import IReporteInstitucionalRepository
from ...domain.entities.reporte_institucional import (
    ReporteInstitucional,
    PosicionEquipo,
    ReporteInstitucionalHistorico,
    EntradaHistorico,
)


class ReporteInstitucionalRepositoryImpl(IReporteInstitucionalRepository):

    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        try:
            return TournamentModel.objects.values_list("state", flat=True).get(pk=torneo_id)
        except TournamentModel.DoesNotExist:
            return None

    def institucion_existe(self, inst_id: str) -> bool:
        from competencia.infrastructure.adapters.output.models import InstitutionModel
        return InstitutionModel.objects.filter(pk=inst_id).exists()

    def obtener_reporte_torneo(
        self, inst_id: str, torneo_id: str
    ) -> Optional[ReporteInstitucional]:
        """
        Una sola query: institución + equipos APROBADO + ranking final.
        """
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    i.id                        AS inst_id,
                    i.name                      AS inst_nombre,
                    i.type                      AS inst_tipo,
                    eq.id                       AS equipo_id,
                    eq.name                     AS equipo_nombre,
                    fr.posicion_final,
                    fr.puntaje_total_acumulado
                FROM competencia_institution i
                INNER JOIN competencia_team eq
                    ON eq.institution_id = i.id
                   AND eq.tournament_id  = %s
                   AND eq.estado_inscripcion = 'APROBADO'
                LEFT JOIN competencia_final_ranking fr
                    ON fr.team_id        = eq.id
                   AND fr.tournament_id  = %s
                WHERE i.id = %s
                ORDER BY fr.posicion_final ASC NULLS LAST
            ''', [torneo_id, torneo_id, inst_id])

            cols  = [c[0] for c in cursor.description]
            filas = [dict(zip(cols, row)) for row in cursor.fetchall()]

        if not filas:
            return None

        posiciones = [
            PosicionEquipo(
                equipo_id=f['equipo_id'],
                nombre_equipo=f['equipo_nombre'],
                posicion_final=f['posicion_final'] or 0,
                puntaje_acumulado=float(f['puntaje_total_acumulado'] or 0),
            )
            for f in filas
        ]

        puntajes = [p.puntaje_acumulado for p in posiciones]
        puntaje_promedio = round(sum(puntajes) / len(puntajes), 4) if puntajes else 0.0
        mejor_posicion = min(
            (p.posicion_final for p in posiciones if p.posicion_final > 0),
            default=0,
        )

        criterio_nombre = self._criterio_mas_destacado(
            torneo_id, [p.equipo_id for p in posiciones]
        )

        return ReporteInstitucional(
            institucion_id=filas[0]['inst_id'],
            nombre_institucion=filas[0]['inst_nombre'],
            tipo=filas[0]['inst_tipo'],
            torneo_id=torneo_id,
            total_equipos_participantes=len(posiciones),
            posiciones_obtenidas=posiciones,
            puntaje_promedio_institucional=puntaje_promedio,
            mejor_posicion_lograda=mejor_posicion,
            criterio_mas_destacado=criterio_nombre,
        )

    def _criterio_mas_destacado(self, torneo_id: str, equipo_ids: list) -> str:
        """
        Criterio con mayor AVG(valor_normalizado) entre los equipos de la institución.
        Solo resultados DEFINITIVE.
        """
        if not equipo_ids:
            return ''
        placeholders = ','.join(['%s'] * len(equipo_ids))
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT c.name, AVG(mr.valor_normalizado) AS promedio
                FROM competencia_match_result mr
                INNER JOIN competencia_criteria c ON c.id = mr.criterio_id
                WHERE mr.equipo_id IN ({placeholders})
                  AND mr.estado_resultado = 'DEFINITIVE'
                  AND c.tournament_id = %s
                GROUP BY c.id, c.name
                ORDER BY promedio DESC
                LIMIT 1
            ''', [*equipo_ids, torneo_id])
            row = cursor.fetchone()
        return row[0] if row else ''

    def obtener_reporte_historico(
        self, inst_id: str
    ) -> Optional[ReporteInstitucionalHistorico]:
        """
        Una sola query: todos los torneos FINISHED donde la institución participó,
        con promedio de puntaje y mejor posición por torneo, ordenado por fecha DESC.
        """
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    i.id                            AS inst_id,
                    i.name                          AS inst_nombre,
                    i.type                          AS inst_tipo,
                    t.id                            AS torneo_id,
                    t.name                          AS torneo_nombre,
                    t.date_end                      AS torneo_fecha,
                    COUNT(DISTINCT eq.id)           AS total_equipos,
                    AVG(fr.puntaje_total_acumulado) AS puntaje_promedio,
                    MIN(fr.posicion_final)          AS mejor_posicion
                FROM competencia_institution i
                INNER JOIN competencia_team eq
                    ON eq.institution_id = i.id
                   AND eq.estado_inscripcion = 'APROBADO'
                INNER JOIN competencia_tournament t
                    ON t.id = eq.tournament_id
                   AND t.state = 'finalized'
                LEFT JOIN competencia_final_ranking fr
                    ON fr.team_id       = eq.id
                   AND fr.tournament_id = t.id
                WHERE i.id = %s
                GROUP BY i.id, i.name, i.type, t.id, t.name, t.date_end
                ORDER BY t.date_end DESC
            ''', [inst_id])

            cols  = [c[0] for c in cursor.description]
            filas = [dict(zip(cols, row)) for row in cursor.fetchall()]

        if not filas:
            return None

        evolucion = [
            EntradaHistorico(
                torneo_id=f['torneo_id'],
                nombre_torneo=f['torneo_nombre'],
                fecha=f['torneo_fecha'].isoformat() if f['torneo_fecha'] else '',
                equipos=f['total_equipos'],
                puntaje_promedio=round(float(f['puntaje_promedio'] or 0), 4),
                mejor_posicion=f['mejor_posicion'] or 0,
            )
            for f in filas
        ]

        return ReporteInstitucionalHistorico(
            institucion_id=filas[0]['inst_id'],
            nombre_institucion=filas[0]['inst_nombre'],
            tipo=filas[0]['inst_tipo'],
            evolucion=evolucion,
        )
