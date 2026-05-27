from simulacion.infrastructure.persistence.reto_analisis_repository import (
    obtener_reto_con_criterios, guardar_analisis,
)
from simulacion.infrastructure.ia.analisis_engine import analizar_entrega


class AnalizarProgramacionUseCase:
    def ejecutar(self, reto_id: str, participante_id: str,
                 torneo_id: str, codigo_fuente: str) -> dict:
        contexto = obtener_reto_con_criterios(reto_id)
        if not contexto or contexto['caso'] != 'PROGRAMACION':
            raise ValueError(f'No existe reto de PROGRAMACION con id={reto_id}')
        resultado = analizar_entrega(codigo_fuente, contexto)
        analisis = guardar_analisis({
            'reto_id':                     reto_id,
            'participante_id':             participante_id,
            'torneo_id':                   torneo_id,
            'caso':                        'PROGRAMACION',
            'contenido_entrega':           codigo_fuente,
            'calificaciones_por_criterio': resultado['calificaciones'],
            'puntaje_total_simulado':      resultado['puntaje_total_simulado'],
            'observacion_general':         resultado.get('observacion_general', ''),
        })
        return {
            'analisis_id':                 str(analisis.id),
            'puntaje_total_simulado':      analisis.puntaje_total_simulado,
            'calificaciones_por_criterio': analisis.calificaciones_por_criterio,
            'observacion_general':         analisis.observacion_general,
        }
