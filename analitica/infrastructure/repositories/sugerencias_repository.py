import uuid
from typing import Optional
from django.db import connection
from django.utils import timezone

from ...domain.ports.sugerencias_repository_port import ISugerenciasRepository
from ...domain.entities.sugerencia_decision import SugerenciaDecision
from ..adapters.output.models import SugerenciaDecisionModel


class SugerenciasRepositoryImpl(ISugerenciasRepository):

    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        try:
            return TournamentModel.objects.values_list("state", flat=True).get(pk=torneo_id)
        except TournamentModel.DoesNotExist:
            return None

    def analizar_retrasos(self, torneo_id: str) -> list[dict]:
        """
        Una sola query: cuenta partidos PENDING con fecha_programada vencida > 20 min.
        """
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT COUNT(*) AS total
                FROM competencia_match
                WHERE tournament_id = %s
                  AND estado = 'PENDING'
                  AND fecha_programada IS NOT NULL
                  AND fecha_programada < NOW() - INTERVAL '20 minutes'
            ''', [torneo_id])
            row = cursor.fetchone()
        total = row[0] if row else 0
        return [{"total": total}] if total > 0 else []

    def analizar_criterios(self, torneo_id: str) -> list[dict]:
        """
        Una sola query: criterios con STDDEV(valor_normalizado) > 40 o < 2.
        Solo resultados DEFINITIVE.
        """
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    c.id   AS criterio_id,
                    c.name AS criterio_nombre,
                    COALESCE(STDDEV(mr.valor_normalizado), 0) AS desv_est
                FROM competencia_criteria c
                INNER JOIN competencia_match_result mr
                    ON mr.criterio_id = c.id
                   AND mr.estado_resultado = 'DEFINITIVE'
                WHERE c.tournament_id = %s
                GROUP BY c.id, c.name
                HAVING STDDEV(mr.valor_normalizado) > 40
                    OR STDDEV(mr.valor_normalizado) < 2
                ORDER BY desv_est DESC
            ''', [torneo_id])
            cols  = [d[0] for d in cursor.description]
            filas = [dict(zip(cols, row)) for row in cursor.fetchall()]
        return [
            {
                "criterio_id":     f["criterio_id"],
                "criterio_nombre": f["criterio_nombre"],
                "desv_est":        float(f["desv_est"]),
            }
            for f in filas
        ]

    def analizar_equipos_bajo_rendimiento(self, torneo_id: str) -> list[dict]:
        """
        Una sola query:
        - Ranking final con PERCENT_RANK para detectar percentil <= 10.
        - JOIN con team y criterios débiles (avg < 50 normalizado).
        Retorna equipos en el 10% inferior.
        """
        with connection.cursor() as cursor:
            # Paso 1: equipos en percentil <= 10
            cursor.execute('''
                SELECT
                    fr.team_id,
                    eq.name AS equipo_nombre,
                    fr.puntaje_total_acumulado,
                    PERCENT_RANK() OVER (
                        ORDER BY fr.puntaje_total_acumulado
                    ) AS percentil
                FROM competencia_final_ranking fr
                INNER JOIN competencia_team eq ON eq.id = fr.team_id
                WHERE fr.tournament_id = %s
            ''', [torneo_id])
            cols  = [d[0] for d in cursor.description]
            todos = [dict(zip(cols, row)) for row in cursor.fetchall()]

        equipos_bajos = [
            f for f in todos if float(f["percentil"]) <= 0.10
        ]
        if not equipos_bajos:
            return []

        # Paso 2: criterios débiles por equipo (avg valor_normalizado < 50)
        resultado = []
        for eq in equipos_bajos:
            criterios_debiles = self._criterios_debiles(torneo_id, eq["team_id"])
            resultado.append({
                "equipo_id":        eq["team_id"],
                "equipo_nombre":    eq["equipo_nombre"],
                "puntaje":          float(eq["puntaje_total_acumulado"]),
                "criterios_debiles": criterios_debiles,
            })
        return resultado

    def _criterios_debiles(self, torneo_id: str, equipo_id: str) -> list[str]:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT c.name
                FROM competencia_criteria c
                INNER JOIN competencia_match_result mr
                    ON mr.criterio_id = c.id
                   AND mr.equipo_id = %s
                   AND mr.estado_resultado = 'DEFINITIVE'
                WHERE c.tournament_id = %s
                GROUP BY c.id, c.name
                HAVING AVG(mr.valor_normalizado) < 50
                ORDER BY AVG(mr.valor_normalizado) ASC
            ''', [equipo_id, torneo_id])
            return [row[0] for row in cursor.fetchall()]

    def upsert_sugerencia(
        self,
        torneo_id: str,
        tipo: str,
        descripcion: str,
        accion_sugerida: str,
        entidad_ref_id: str,
        severidad: str,
    ) -> SugerenciaDecision:
        """
        get_or_create por (torneo_id, tipo, entidad_ref_id).
        Si existe como PENDIENTE actualiza descripcion y accion_sugerida.
        Si existe como ATENDIDA/DESCARTADA no modifica nada.
        """
        try:
            obj = SugerenciaDecisionModel.objects.get(
                torneo_id=torneo_id,
                tipo=tipo,
                entidad_ref_id=entidad_ref_id,
            )
            if obj.estado == 'PENDIENTE':
                obj.descripcion    = descripcion
                obj.accion_sugerida = accion_sugerida
                obj.save(update_fields=['descripcion', 'accion_sugerida'])
        except SugerenciaDecisionModel.DoesNotExist:
            obj = SugerenciaDecisionModel.objects.create(
                torneo_id=torneo_id,
                tipo=tipo,
                descripcion=descripcion,
                accion_sugerida=accion_sugerida,
                entidad_ref_id=entidad_ref_id,
                severidad=severidad,
                estado='PENDIENTE',
            )
        return self._to_entity(obj)

    def obtener_pendientes(self, torneo_id: str) -> list[SugerenciaDecision]:
        qs = SugerenciaDecisionModel.objects.filter(
            torneo_id=torneo_id,
            estado='PENDIENTE',
        ).order_by('generado_en')
        return [self._to_entity(obj) for obj in qs]

    @staticmethod
    def _to_entity(obj: SugerenciaDecisionModel) -> SugerenciaDecision:
        return SugerenciaDecision(
            id=str(obj.id),
            torneo_id=obj.torneo_id,
            tipo=obj.tipo,
            descripcion=obj.descripcion,
            accion_sugerida=obj.accion_sugerida,
            entidad_ref_id=obj.entidad_ref_id,
            severidad=obj.severidad,
            estado=obj.estado,
            generado_en=obj.generado_en.isoformat() if obj.generado_en else '',
        )
