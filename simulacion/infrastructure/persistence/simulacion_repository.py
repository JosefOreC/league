from typing import List
from django.db import connection

from simulacion.domain.entities.simulacion_predictiva import SimulacionPredictivaEntity
from simulacion.domain.ports.simulacion_repository import SimulacionRepositoryPort
from simulacion.infrastructure.adapters.output.models import SimulacionPredictiva, SimulacionResultado


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

    def obtener_historial(self, participante_id: int) -> List[dict]:  # type: ignore[override]
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


def obtener_contexto_torneo(tournament_id: str, user_id: str) -> dict:
    """
    Una sola query. Trae criterios + equipo del líder + total equipos aprobados.
    Lanza PermissionError si el user_id no es representante de un equipo aprobado.
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                c.id                        AS criterio_id,
                c.name                      AS criterio_nombre,
                c.description               AS criterio_descripcion,
                c.value                     AS peso,
                c.min_value_qualification,
                c.max_value_qualification,
                t.name                      AS torneo_nombre,
                t.description               AS torneo_descripcion,
                t.category,
                eq.id                       AS equipo_id,
                eq.name                     AS equipo_nombre,
                eq.nivel_tecnico_declarado,
                (
                    SELECT COUNT(*)
                    FROM competencia_team t2
                    WHERE t2.tournament_id = t.id
                      AND t2.estado_inscripcion = 'APROBADO'
                ) AS total_equipos_aprobados
            FROM competencia_criteria c
            INNER JOIN competencia_tournament t
                ON t.id = c.tournament_id
            INNER JOIN competencia_team eq
                ON eq.tournament_id = t.id
               AND eq.representante_id = %s
               AND eq.estado_inscripcion = 'APROBADO'
            WHERE c.tournament_id = %s
            ORDER BY c.value DESC
        ''', [user_id, tournament_id])

        cols  = [col[0] for col in cursor.description]
        filas = [dict(zip(cols, row)) for row in cursor.fetchall()]

    if not filas:
        raise PermissionError('No tiene un equipo aprobado en este torneo')

    return {
        'torneo_nombre':      filas[0]['torneo_nombre'],
        'torneo_descripcion': filas[0]['torneo_descripcion'],
        'torneo_estado':      filas[0].get('torneo_estado', ''),
        'category':           filas[0].get('category', ''),
        'equipo_id':          filas[0]['equipo_id'],
        'equipo_nombre':      filas[0].get('equipo_nombre', ''),
        'nivel_tecnico':      filas[0]['nivel_tecnico_declarado'],
        'total_equipos':      filas[0]['total_equipos_aprobados'],
        'criterios': [
            {k: f[k] for k in ('criterio_id', 'criterio_nombre', 'criterio_descripcion',
                                'peso', 'min_value_qualification', 'max_value_qualification')}
            for f in filas
        ],
    }


def guardar_resultado(datos: dict) -> SimulacionResultado:
    return SimulacionResultado.objects.create(**datos)
