import uuid
from simulacion.infrastructure.persistence.simulacion_repository import (
    obtener_contexto_torneo, guardar_resultado,
)
from simulacion.infrastructure.ia.scoring_engine import ejecutar_scoring, calcular_scores


def calcular_posicion(puntaje_total: float, nivel_tecnico: str, total_equipos: int) -> dict:
    DISTRIBUCIONES = {
        'BASICO':     [30, 45, 55, 65, 75, 85, 95],
        'INTERMEDIO': [40, 52, 62, 70, 78, 86, 94],
        'AVANZADO':   [50, 60, 68, 75, 82, 89, 96],
    }
    dist = DISTRIBUCIONES.get(nivel_tecnico, DISTRIBUCIONES['INTERMEDIO'])

    equipos_mejores = sum(1 for ref in dist if ref > puntaje_total)
    posicion = max(1, round(equipos_mejores / len(dist) * total_equipos) + 1)
    posicion = min(posicion, total_equipos)

    percentil = round((1 - (posicion - 1) / max(total_equipos, 1)) * 100, 1)

    resultado = {
        'posicion_estimada': posicion,
        'total_equipos':     total_equipos,
        'percentil':         percentil,
    }
    if total_equipos == 1:
        resultado['advertencia'] = 'Estimación con muestra única'

    return resultado


def calcular_fortalezas_debilidades(scores: list, total_criterios: int) -> tuple:
    top_n = 3 if total_criterios > 3 else max(1, total_criterios // 2)

    ordenados = sorted(
        scores,
        key=lambda s: (-s['valor_normalizado'], -s['peso'], s['nombre'])
    )

    fortalezas = [
        {
            'criterio_id':       s['criterio_id'],
            'nombre':            s['nombre'],
            'valor_normalizado': s['valor_normalizado'],
            'motivo':            'Mejor desempeño relativo',
        }
        for s in ordenados[:top_n]
    ]

    ids_fortalezas = {s['criterio_id'] for s in ordenados[:top_n]}
    candidatos_deb = [s for s in ordenados if s['criterio_id'] not in ids_fortalezas]
    candidatos_deb_sorted = sorted(
        candidatos_deb,
        key=lambda s: (s['valor_normalizado'], -s['peso'], s['nombre'])
    )

    debilidades = []
    for s in candidatos_deb_sorted[:top_n]:
        motivo = ('Puntaje por debajo del 50% del rango máximo del criterio'
                  if s['valor_normalizado'] < 50 else 'Área de mejora')
        debilidades.append({
            'criterio_id':       s['criterio_id'],
            'nombre':            s['nombre'],
            'valor_normalizado': s['valor_normalizado'],
            'motivo':            motivo,
        })

    return fortalezas, debilidades


def generar_retroalimentacion(puntaje_total: float, posicion: int,
                               total_equipos: int, fortalezas: list,
                               debilidades: list) -> dict:
    todos_sobre_80 = all(f['valor_normalizado'] >= 80 for f in fortalezas) and not debilidades

    if todos_sobre_80:
        resumen = (
            f"Excelente desempeño. Tu equipo obtuvo {puntaje_total} puntos, "
            f"posicionándose estimado en el lugar {posicion} de {total_equipos} equipos. "
            f"Todos los criterios superan el 80% del rango máximo."
        )
        return {
            'resumen':              resumen,
            'recomendaciones':      [],
            'sin_mejoras_criticas': True,
        }

    resumen = (
        f"Tu equipo obtuvo un puntaje simulado de {puntaje_total} sobre 100, "
        f"con una posición estimada de {posicion} entre {total_equipos} equipos. "
        f"Hay criterios clave que pueden mejorar antes del torneo."
    )

    recomendaciones = [
        f"Mejorar '{d['nombre']}': {d['motivo'].lower()}. "
        f"Actualmente en {d['valor_normalizado']:.1f}% del rango máximo."
        for d in debilidades
    ]

    return {
        'resumen':              resumen,
        'recomendaciones':      recomendaciones,
        'sin_mejoras_criticas': False,
    }


class EjecutarSimulacionUseCase:

    def ejecutar(self, tournament_id: str, user_id: str, entregable: str) -> dict:

        if not entregable or not entregable.strip():
            raise ValueError('campo:entregable:requerido')
        if len(entregable.strip()) < 100:
            raise ValueError(f'longitud:{len(entregable.strip())}')

        ctx = obtener_contexto_torneo(tournament_id, user_id)

        scores_raw    = ejecutar_scoring(
            entregable.strip(),
            ctx['criterios'],
            torneo_nombre=ctx['torneo_nombre'],
            torneo_descripcion=ctx['torneo_descripcion'],
        )
        scores, total = calcular_scores(scores_raw, ctx['criterios'])

        posicion_data = calcular_posicion(total, ctx['nivel_tecnico'], ctx['total_equipos'])

        fortalezas, debilidades = calcular_fortalezas_debilidades(scores, len(ctx['criterios']))

        retro = generar_retroalimentacion(
            total, posicion_data['posicion_estimada'],
            posicion_data['total_equipos'], fortalezas, debilidades,
        )

        guardar_resultado({
            'tournament_id':         tournament_id,
            'equipo_id':             ctx['equipo_id'],
            'entregable':            entregable.strip(),
            'scores':                scores,
            'puntaje_total':         total,
            'posicion_estimada':     posicion_data['posicion_estimada'],
            'total_equipos':         posicion_data['total_equipos'],
            'percentil':             posicion_data['percentil'],
            'advertencia_muestra':   posicion_data.get('advertencia', ''),
            'fortalezas':            fortalezas,
            'debilidades':           debilidades,
            'retro_resumen':         retro['resumen'],
            'retro_recomendaciones': retro['recomendaciones'],
            'sin_mejoras_criticas':  retro['sin_mejoras_criticas'],
        })

        return {
            'simulation_id': str(uuid.uuid4()),
            'scores':        scores,
            'puntaje_total': total*100,
            **posicion_data,
            'fortalezas':    fortalezas,
            'debilidades':   debilidades,
            'retroalimentacion': {
                'resumen':              retro['resumen'],
                'recomendaciones':      retro['recomendaciones'],
                'sin_mejoras_criticas': retro['sin_mejoras_criticas'],
            },
        }
