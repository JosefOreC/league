from simulacion.infrastructure.persistence.reto_analisis_repository import (
    obtener_reto_con_criterios, guardar_analisis,
)
from simulacion.infrastructure.ia.analisis_engine import analizar_entrega


class AnalizarComponentesUseCase:
    def ejecutar(self, reto_id: str, participante_id: str,
                 torneo_id: str, descripcion_solucion: str) -> dict:
        contexto = obtener_reto_con_criterios(torneo_id, 'COMPONENTES')
        if not contexto or not contexto['criterios']:
            raise ValueError(f'No existe torneo con criterios de COMPONENTES con id={torneo_id}')
        resultado = analizar_entrega(descripcion_solucion, contexto)
        analisis = guardar_analisis({
            'reto_id':                     reto_id,
            'participante_id':             participante_id,
            'torneo_id':                   torneo_id,
            'caso':                        'COMPONENTES',
            'contenido_entrega':           descripcion_solucion,
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
