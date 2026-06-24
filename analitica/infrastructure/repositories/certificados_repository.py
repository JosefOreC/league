from typing import Optional
from django.db import connection

from ...domain.ports.certificados_repository_port import ICertificadosRepository
from ...domain.entities.certificado_digital import (
    CertificadoDigital,
    DatosParticipante,
    DatosGanador,
)
from ..adapters.output.models import CertificadoDigitalModel


class CertificadosRepositoryImpl(ICertificadosRepository):

    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        from competencia.infrastructure.adapters.output.models import TournamentModel
        try:
            return TournamentModel.objects.values_list("state", flat=True).get(pk=torneo_id)
        except TournamentModel.DoesNotExist:
            return None

    def obtener_participantes(self, torneo_id: str) -> list[DatosParticipante]:
        """
        Una sola query: participantes + equipo + institución + torneo.
        Solo equipos con estado_inscripcion = 'APROBADO'.
        """
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    p.id                AS participante_id,
                    p.nombres,
                    p.apellidos,
                    p.autorizacion_datos,
                    eq.id               AS equipo_id,
                    eq.name             AS equipo_nombre,
                    i.name              AS institucion_nombre,
                    t.name              AS torneo_nombre,
                    t.date_start        AS torneo_fecha
                FROM competencia_participant p
                INNER JOIN competencia_team eq
                    ON eq.id = p.team_id
                   AND eq.tournament_id = %s
                   AND eq.estado_inscripcion = 'APROBADO'
                INNER JOIN competencia_institution i
                    ON i.id = eq.institution_id
                INNER JOIN competencia_tournament t
                    ON t.id = eq.tournament_id
                ORDER BY eq.name, p.apellidos, p.nombres
            ''', [torneo_id])
            cols  = [c[0] for c in cursor.description]
            filas = [dict(zip(cols, row)) for row in cursor.fetchall()]

        return [
            DatosParticipante(
                participante_id=f['participante_id'],
                nombres=f['nombres'],
                apellidos=f['apellidos'],
                autorizacion_datos=bool(f['autorizacion_datos']),
                equipo_id=f['equipo_id'],
                equipo_nombre=f['equipo_nombre'],
                institucion_nombre=f['institucion_nombre'],
                torneo_nombre=f['torneo_nombre'],
                torneo_fecha=f['torneo_fecha'].isoformat() if f['torneo_fecha'] else '',
            )
            for f in filas
        ]

    def obtener_datos_ganador(
        self, torneo_id: str, equipo_id: str
    ) -> Optional[DatosGanador]:
        """
        Dos queries:
        1. Datos del equipo desde final_ranking + institución + torneo.
        2. Lista de participantes del equipo.
        """
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    eq.id               AS equipo_id,
                    eq.name             AS equipo_nombre,
                    i.name              AS institucion_nombre,
                    t.name              AS torneo_nombre,
                    t.date_start        AS torneo_fecha,
                    fr.posicion_final,
                    fr.puntaje_total_acumulado,
                    fr.medalla,
                    COALESCE(fr.mencion_especial, '') AS mencion_especial
                FROM competencia_final_ranking fr
                INNER JOIN competencia_team eq
                    ON eq.id = fr.team_id
                INNER JOIN competencia_institution i
                    ON i.id = eq.institution_id
                INNER JOIN competencia_tournament t
                    ON t.id = fr.tournament_id
                WHERE fr.tournament_id = %s
                  AND fr.team_id       = %s
                  AND fr.medalla IS NOT NULL
            ''', [torneo_id, equipo_id])
            cols = [c[0] for c in cursor.description]
            fila = cursor.fetchone()

        if not fila:
            return None

        datos = dict(zip(cols, fila))

        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT nombres, apellidos
                FROM competencia_participant
                WHERE team_id = %s
                ORDER BY apellidos, nombres
            ''', [equipo_id])
            participantes = [(row[0], row[1]) for row in cursor.fetchall()]

        return DatosGanador(
            equipo_id=datos['equipo_id'],
            equipo_nombre=datos['equipo_nombre'],
            institucion_nombre=datos['institucion_nombre'],
            torneo_nombre=datos['torneo_nombre'],
            torneo_fecha=datos['torneo_fecha'].isoformat() if datos['torneo_fecha'] else '',
            posicion_final=datos['posicion_final'],
            puntaje_total_acumulado=float(datos['puntaje_total_acumulado']),
            medalla=datos['medalla'],
            mencion_especial=datos['mencion_especial'],
            participantes=participantes,
        )

    def guardar_certificado(
        self,
        torneo_id: str,
        tipo_certificado: str,
        nombres_destinatario: str,
        institucion: str,
        codigo_verificacion: str,
        participante_id: Optional[str],
        equipo_id: Optional[str],
        posicion_final: Optional[int],
        medalla: Optional[str],
    ) -> CertificadoDigital:
        obj = CertificadoDigitalModel.objects.create(
            torneo_id=torneo_id,
            tipo_certificado=tipo_certificado,
            nombres_destinatario=nombres_destinatario,
            institucion=institucion,
            codigo_verificacion=codigo_verificacion,
            participante_id=participante_id,
            equipo_id=equipo_id,
            posicion_final=posicion_final,
            medalla=medalla,
        )
        return CertificadoDigital(
            id=str(obj.id),
            torneo_id=obj.torneo_id,
            tipo_certificado=obj.tipo_certificado,
            nombres_destinatario=obj.nombres_destinatario,
            institucion=obj.institucion,
            codigo_verificacion=obj.codigo_verificacion,
            generado_en=obj.generado_en.isoformat() if obj.generado_en else '',
            participante_id=obj.participante_id,
            equipo_id=obj.equipo_id,
            posicion_final=obj.posicion_final,
            medalla=obj.medalla,
        )
