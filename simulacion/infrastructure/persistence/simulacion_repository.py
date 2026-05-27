from typing import List
from django.db import connection

from simulacion.domain.entities.simulacion_predictiva import SimulacionPredictivaEntity
from simulacion.domain.ports.simulacion_repository import SimulacionRepositoryPort
from simulacion.infrastructure.adapters.output.models import SimulacionPredictiva


class SimulacionRepository(SimulacionRepositoryPort):

    def guardar(self, entidad: SimulacionPredictivaEntity) -> SimulacionPredictiva:
        return SimulacionPredictiva.objects.create(
            participante_id=entidad.participante_id,
            torneo_id=entidad.torneo_id,
            tiempo_estimado=entidad.tiempo_estimado,
            complejidad_codigo=entidad.complejidad_codigo,
            colisiones_historicas=entidad.colisiones_historicas,
            telemetria_json=entidad.telemetria_json,
            puntaje_estimado=entidad.puntaje_estimado,
            tiempo_probable_fin=entidad.tiempo_probable_fin,
            rmse_validacion=entidad.rmse_validacion,
            modelo_version=entidad.modelo_version,
            es_oficial=entidad.es_oficial,
        )

    def obtener_historial(self, participante_id: int) -> List[dict]:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    sp.id,
                    sp.puntaje_estimado,
                    sp.tiempo_probable_fin,
                    sp.rmse_validacion,
                    sp.creado_en,
                    t.name  AS torneo_nombre,
                    u.name  AS participante_nombre
                FROM simulacion_predictiva sp
                INNER JOIN competencia_tournament t ON t.id::text = sp.torneo_id::text
                INNER JOIN authentication_user u    ON u.id::text = sp.participante_id::text
                WHERE sp.participante_id = %s
                ORDER BY sp.creado_en DESC
            ''', [participante_id])
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, fila)) for fila in cursor.fetchall()]
