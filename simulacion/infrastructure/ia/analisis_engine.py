from openai import OpenAI
import json
import os

MODEL = "openrouter/auto"
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ['OPENROUTER_API_KEY'],
        )
    return _client

SYSTEM_PROGRAMACION = """
Eres un evaluador técnico de código para torneos de robótica escolar.
Recibirás el código fuente del participante y el reto con sus criterios de evaluación.
Evalúa el código contra cada criterio y responde SOLO con JSON, sin texto adicional:
{
  "calificaciones": [
    {
      "criterio_id": "string",
      "criterio_nombre": "string",
      "calificacion_simulada": float (dentro del rango min–max del criterio),
      "observacion": "qué cumple y qué le falta al código respecto a este criterio"
    }
  ],
  "puntaje_total_simulado": float (0.0 a 100.0, promedio ponderado por peso),
  "observacion_general": "resumen del análisis del código"
}
"""

SYSTEM_COMPONENTES = """
Eres un evaluador técnico de arquitectura y componentes para torneos de robótica escolar.
Recibirás la descripción de la solución del participante y el reto con sus criterios.
Evalúa los componentes contra cada criterio y responde SOLO con JSON, sin texto adicional:
{
  "calificaciones": [
    {
      "criterio_id": "string",
      "criterio_nombre": "string",
      "calificacion_simulada": float (dentro del rango min–max del criterio),
      "observacion": "qué componentes cumple y cuáles faltan o están mal integrados"
    }
  ],
  "puntaje_total_simulado": float (0.0 a 100.0, promedio ponderado por peso),
  "observacion_general": "resumen del análisis de arquitectura y componentes"
}
"""


def analizar_entrega(contenido: str, contexto: dict) -> dict:
    caso   = contexto['caso']
    system = SYSTEM_PROGRAMACION if caso == 'PROGRAMACION' else SYSTEM_COMPONENTES

    criterios_txt = '\n'.join(
        f"- {c['criterio_nombre']} (peso {c['peso']}%, "
        f"rango {c['min_value_qualification']}–{c['max_value_qualification']}): "
        f"{c['criterio_descripcion']}"
        for c in contexto['criterios']
    )
    user_msg = f"""
Reto: {contexto['reto_titulo']}
Descripción del reto: {contexto['reto_descripcion']}
Categoría del torneo: {contexto['categoria']}
Componentes requeridos: {contexto['validation_list']}

Criterios a evaluar:
{criterios_txt}

Entrega del participante:
{contenido}
"""
    response = _get_client().chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg},
        ],
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace('```json', '').replace('```', '').strip()
    return json.loads(raw)
