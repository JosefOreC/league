from typing import List, Optional
from django.db import connection
from simulacion.infrastructure.adapters.output.models import AnalisisEntrega

KEYWORDS_COMPONENTES = {
    'sensor', 'motor', 'actuador', 'chasis', 'estructura', 'rueda',
    'batería', 'electronico', 'hardware', 'cable', 'servo', 'componente',
}
KEYWORDS_PROGRAMACION = {
    'algoritmo', 'código', 'función', 'control', 'lógica', 'bucle',
    'velocidad', 'navegación', 'programación', 'software', 'instrucción',
}


def clasificar_criterio(nombre: str, descripcion: str) -> Optional[str]:
    texto   = (nombre + ' ' + descripcion).lower()
    es_comp = any(k in texto for k in KEYWORDS_COMPONENTES)
    es_prog = any(k in texto for k in KEYWORDS_PROGRAMACION)
    if es_comp and not es_prog: return 'COMPONENTES'
    if es_prog and not es_comp: return 'PROGRAMACION'
    if es_comp and es_prog:     return 'COMPONENTES'
    return None


def obtener_retos_del_torneo(torneo_id: str) -> List[dict]:
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                t.id                      AS torneo_id,
                t.name                    AS torneo_nombre,
                t.description             AS reto_descripcion,
                t.category                AS categoria,
                t.config_tournament,
                c.id                      AS criterio_id,
                c.name                    AS criterio_nombre,
                c.description             AS criterio_descripcion,
                c.value                   AS peso,
                c.min_value_qualification,
                c.max_value_qualification,
                tr.validation_list
            FROM competencia_tournament t
            INNER JOIN competencia_criteria c
                ON c.tournament_id = t.id
            INNER JOIN competencia_tournament_rule tr
                ON tr.id = t.tournament_rule_id
            WHERE t.id = %s
            ORDER BY c.value DESC
        ''', [torneo_id])
        cols = [col[0] for col in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


def obtener_reto_con_criterios(torneo_id: str, caso: str) -> dict:
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                t.id              AS torneo_id,
                t.name            AS reto_titulo,
                t.description     AS reto_descripcion,
                t.category        AS categoria,
                c.id              AS criterio_id,
                c.name            AS criterio_nombre,
                c.description     AS criterio_descripcion,
                c.value           AS peso,
                c.min_value_qualification,
                c.max_value_qualification,
                tr.validation_list
            FROM competencia_tournament t
            INNER JOIN competencia_criteria c
                ON c.tournament_id = t.id
            INNER JOIN competencia_tournament_rule tr
                ON tr.id = t.tournament_rule_id
            WHERE t.id = %s
            ORDER BY c.value DESC
        ''', [torneo_id])
        cols  = [col[0] for col in cursor.description]
        filas = [dict(zip(cols, row)) for row in cursor.fetchall()]

    if not filas:
        return {}

    criterios_filtrados = [
        {k: f[k] for k in (
            'criterio_id', 'criterio_nombre', 'criterio_descripcion',
            'peso', 'min_value_qualification', 'max_value_qualification',
        )}
        for f in filas
        if clasificar_criterio(f['criterio_nombre'], f['criterio_descripcion']) == caso
    ]

    return {
        'reto_id':          torneo_id,
        'reto_titulo':      filas[0]['reto_titulo'],
        'reto_descripcion': filas[0]['reto_descripcion'],
        'caso':             caso,
        'torneo_id':        torneo_id,
        'categoria':        filas[0]['categoria'],
        'validation_list':  filas[0]['validation_list'],
        'criterios':        criterios_filtrados,
    }


def guardar_analisis(datos: dict) -> AnalisisEntrega:
    return AnalisisEntrega.objects.create(**datos)


def listar_analisis(participante_id: str, torneo_id: str) -> List[AnalisisEntrega]:
    return list(
        AnalisisEntrega.objects.filter(
            participante_id=participante_id,
            torneo_id=torneo_id,
        ).order_by('-creado_en')
    )
