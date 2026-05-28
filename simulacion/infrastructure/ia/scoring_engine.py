from openai import OpenAI
import json
import os

MODEL = 'openrouter/auto'
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=os.environ['OPENROUTER_API_KEY'],
        )
    return _client

SYSTEM_SCORING = """Eres un jurado evaluador de torneos de robotica escolar.
Dado un entregable y criterios de evaluacion, asigna un valor_simulado a cada criterio.
Responde SOLO con JSON valido, sin texto adicional ni markdown:
{"scores": [{"criterio_id": "string", "valor_simulado": float}, ...]}
Cada valor_simulado debe estar dentro del rango [min_value_qualification, max_value_qualification]."""


def ejecutar_scoring(entregable: str, criterios: list,
                     torneo_nombre: str = '', torneo_descripcion: str = '') -> list:
    criterios_txt = '\n'.join(
        f"- ID:{c['criterio_id']} | {c['criterio_nombre']}: {c['criterio_descripcion']} "
        f"(rango:{c['min_value_qualification']}-{c['max_value_qualification']}, peso:{c['peso']}%)"
        for c in criterios
    )
    user_content = (
        f"Torneo: {torneo_nombre}\n"
        f"Reto/Objetivo: {torneo_descripcion}\n\n"
        f"Criterios a evaluar:\n{criterios_txt}\n\n"
        f"Entregable del participante:\n{entregable}"
    )
    response = _get_client().chat.completions.create(
        model=MODEL,
        temperature=0,
        seed=42,
        messages=[
            {'role': 'system', 'content': SYSTEM_SCORING},
            {'role': 'user',   'content': user_content},
        ],
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace('```json', '').replace('```', '').strip()
    return json.loads(raw)['scores']


def calcular_scores(scores_raw: list, criterios: list) -> tuple:
    """
    Retorna (scores_completos, puntaje_total).
    puntaje_total = Σ (valor_normalizado_i × peso_i / 100), redondeado a 2 decimales.
    """
    criterios_map = {c['criterio_id']: c for c in criterios}
    scores = []

    for s in scores_raw:
        c   = criterios_map[s['criterio_id']]
        v   = float(s['valor_simulado'])
        v   = max(float(c['min_value_qualification']),
                  min(float(c['max_value_qualification']), v))
        rng = float(c['max_value_qualification']) - float(c['min_value_qualification'])
        v_norm = ((v - float(c['min_value_qualification'])) / rng * 100) if rng > 0 else 0.0

        scores.append({
            'criterio_id':       c['criterio_id'],
            'nombre':            c['criterio_nombre'],
            'peso':              float(c['peso']),
            'valor_simulado':    round(v, 4),
            'valor_normalizado': round(v_norm, 4),
            'en_rango':          True,
        })

    puntaje_total = round(
        sum(s['valor_normalizado'] * s['peso'] / 100 for s in scores), 2
    )
    return scores, puntaje_total
