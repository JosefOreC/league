"""
Motor de scoring heurístico determinista — HU-SIM-02, HU-SIM-03, HU-SIM-04, HU-SIM-05.

Algoritmo (sin LLM, sin dependencias externas):
  1. Calidad base del texto: ratio de longitud y riqueza léxica.
  2. Score por criterio: solapamiento de palabras clave del criterio vs. entregable.
  3. Normalización al rango [min_qualification, max_qualification] del criterio.
  4. puntaje_total = Σ(valor_normalizado_i × peso_i / 100), redondeado a 2 dec.
  5. Posición estimada (HU-SIM-03): mapeo lineal contra distribución de referencia
     ajustada por nivel_tecnico_declarado.
  6. Fortalezas / debilidades (HU-SIM-04): top-N / bottom-N por valor_normalizado;
     tiebreak: mayor peso → orden alfabético.
  7. Retroalimentación (HU-SIM-05): plantillas en español (es-PE), deterministas.

Determinismo garantizado: no usa random(), time() ni estado mutable compartido.
simulation_id: UUID v5 derivado de (tournament_id, team_id, entregable).
"""
import re
import uuid
from math import ceil
from typing import List, Tuple

from simulacion.domain.entities.criterion_score import CriterionScore
from simulacion.domain.entities.simulation_context import SimulationContext
from simulacion.domain.entities.simulation_result import (
    FortalezaDebilidad,
    PosicionEstimada,
    Retroalimentacion,
    SimulationResult,
)
from simulacion.domain.ports.scoring_engine_port import ScoringEnginePort

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Namespace fijo para generar simulation_id determinista (UUID v5)
_SIM_NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

# Stop-words básicas en español para filtrar keywords sin valor semántico
_STOP_WORDS: frozenset = frozenset({
    "de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas",
    "y", "o", "e", "ni", "pero", "si", "que", "en", "con", "por", "para",
    "al", "se", "su", "sus", "es", "son", "fue", "ser", "estar", "hay",
    "no", "mas", "más", "ya", "le", "les", "me", "mi", "tu", "a", "lo",
    "como", "cuando", "donde", "porque", "también", "este", "esta",
    "estos", "estas", "ese", "esa", "esos", "esas", "ante", "bajo",
    "cabe", "entre", "hacia", "hasta", "según", "sin", "sobre", "tras",
})

# Referencia de puntaje esperado por nivel técnico (para HU-SIM-03)
_NIVEL_BASELINE: dict = {
    "BASICO": 38.0,
    "INTERMEDIO": 58.0,
    "AVANZADO": 75.0,
}

# Mínimo de caracteres del entregable (≥100 ya validado en el use case)
_MAX_REF_LENGTH = 1500.0  # longitud de referencia para saturar length_score


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    """Extrae tokens alfabéticos ≥3 caracteres, sin stop-words, en minúsculas."""
    words = re.findall(r"\b[a-záéíóúüñ]{3,}\b", text.lower())
    return [w for w in words if w not in _STOP_WORDS]


def _base_quality(entregable: str) -> float:
    """
    Calidad base del texto, en [0, 1].
    Combina:
      - length_score:    qué tan largo es el texto (satura a _MAX_REF_LENGTH).
      - richness_score:  ratio palabras únicas / total (riqueza léxica).
    """
    words = entregable.lower().split()
    if not words:
        return 0.0
    length_score = min(len(entregable) / _MAX_REF_LENGTH, 1.0)
    richness_score = len(set(words)) / len(words)
    return round(0.45 * length_score + 0.55 * richness_score, 6)


def _criterion_keyword_score(
    entregable_tokens: frozenset,
    criterion_name: str,
    criterion_description: str,
) -> float:
    """
    Score de solapamiento de keywords del criterio contra el entregable, en [0, 1].
    Keywords = tokens del name + description del criterio.
    """
    criterion_text = f"{criterion_name} {criterion_description}"
    keywords = _tokenize(criterion_text)
    if not keywords:
        return 0.5  # neutral si el criterio no tiene keywords útiles
    matched = sum(1 for kw in keywords if kw in entregable_tokens)
    return min(matched / len(keywords), 1.0)


def _compute_valor_simulado(
    combined_score: float,
    min_q: float,
    max_q: float,
) -> float:
    """Mapea combined_score [0,1] al rango [min_q, max_q] del criterio."""
    if max_q <= min_q:
        return min_q
    return round(min_q + combined_score * (max_q - min_q), 4)


def _compute_valor_normalizado(
    valor_simulado: float,
    min_q: float,
    max_q: float,
) -> float:
    """Normaliza valor_simulado a porcentaje [0, 100] dentro del rango."""
    if max_q <= min_q:
        return 0.0
    return round((valor_simulado - min_q) / (max_q - min_q) * 100, 4)


def _sort_key_desc(score: CriterionScore) -> Tuple:
    """Clave de orden descendente: mayor valor_normalizado, luego mayor peso, luego nombre asc."""
    return (-score.valor_normalizado, -score.peso, score.nombre)


def _sort_key_asc(score: CriterionScore) -> Tuple:
    """Clave de orden ascendente: menor valor_normalizado, luego mayor peso (tiebreak), luego nombre asc."""
    return (score.valor_normalizado, -score.peso, score.nombre)


def _split_fortalezas_debilidades(
    scores: List[CriterionScore],
) -> Tuple[List[CriterionScore], List[CriterionScore]]:
    """
    HU-SIM-04: Divide scores en fortalezas (top) y debilidades (bottom).
    Reglas:
      - n <= 1: fortalezas=scores, debilidades=[]
      - n <= 3: top 1 y bottom 1
      - n >= 4: top min(3, n//2) y bottom min(3, n - top)
      - Ningún criterio aparece en ambos grupos.
    Tiebreak: mayor peso → nombre alfabético ascendente.
    """
    n = len(scores)
    if n == 0:
        return [], []
    if n == 1:
        return list(scores), []

    by_desc = sorted(scores, key=_sort_key_desc)
    by_asc = sorted(scores, key=_sort_key_asc)

    if n <= 3:
        num_top = 1
        num_bot = 1
    else:
        num_top = min(3, n // 2)
        num_bot = min(3, n - num_top)

    top_ids = {s.criterio_id for s in by_desc[:num_top]}
    bot_candidates = [s for s in by_asc if s.criterio_id not in top_ids]

    return by_desc[:num_top], bot_candidates[:num_bot]


def _build_fortaleza_debilidad(
    score: CriterionScore,
    is_weakness: bool,
    min_q: float,
) -> FortalezaDebilidad:
    motivo_debilidad = (
        "Puntaje por debajo del 50% del rango máximo del criterio"
        if is_weakness and score.valor_normalizado < 50.0
        else "Criterio con menor desempeño relativo"
    )
    motivo_fortaleza = "Criterio con mayor desempeño relativo"
    return FortalezaDebilidad(
        criterio_id=score.criterio_id,
        nombre=score.nombre,
        valor_normalizado=score.valor_normalizado,
        motivo=motivo_debilidad if is_weakness else motivo_fortaleza,
    )


def _compute_posicion(
    puntaje_total: float,
    nivel_tecnico: str,
    total_equipos: int,
) -> PosicionEstimada:
    """
    HU-SIM-03: Calcula posición estimada.
    El puntaje_total (0-100) se ajusta por nivel_tecnico para reflejar
    la dificultad de la competencia. Luego se mapea linealmente a posición.
    """
    if total_equipos <= 0:
        total_equipos = 1

    # Ajuste competitivo por nivel (equipos más avanzados compiten más fuerte)
    nivel_penalty = {"BASICO": 5.0, "INTERMEDIO": 0.0, "AVANZADO": -8.0}
    adjusted = puntaje_total + nivel_penalty.get(nivel_tecnico, 0.0)
    adjusted = max(0.0, min(100.0, adjusted))

    percentil = round(adjusted, 1)

    if total_equipos == 1:
        return PosicionEstimada(
            posicion_estimada=1,
            total_equipos=1,
            percentil=percentil,
            advertencia="Estimación con muestra única",
        )

    # Posición: cuántos equipos superan nuestro score en la distribución uniforme
    posicion = max(1, ceil((1.0 - adjusted / 100.0) * total_equipos))
    return PosicionEstimada(
        posicion_estimada=posicion,
        total_equipos=total_equipos,
        percentil=percentil,
    )


def _build_retroalimentacion(
    puntaje_total: float,
    posicion: PosicionEstimada,
    debilidades: List[FortalezaDebilidad],
    scores: List[CriterionScore],
) -> Retroalimentacion:
    """
    HU-SIM-05: Genera retroalimentación determinista en español (es-PE).
    Sin LLM; usa plantillas de texto parametrizadas.
    """
    all_above_80 = all(s.valor_normalizado >= 80.0 for s in scores)

    adv_txt = f" ({posicion.advertencia})" if posicion.advertencia else ""
    resumen = (
        f"Tu equipo obtuvo un puntaje total simulado de {puntaje_total:.2f}/100, "
        f"lo que lo ubica en la posición estimada {posicion.posicion_estimada} "
        f"de {posicion.total_equipos} equipos "
        f"(percentil {posicion.percentil:.1f}){adv_txt}."
    )

    if all_above_80:
        return Retroalimentacion(
            resumen=resumen + " El desempeño global es sobresaliente en todos los criterios.",
            recomendaciones=[],
            sin_mejoras_criticas=True,
        )

    recomendaciones: List[str] = []
    for deb in debilidades:
        recomendaciones.append(
            f"Refuerza el criterio '{deb.nombre}': obtuvo {deb.valor_normalizado:.1f}% "
            f"del rango máximo. {deb.motivo}."
        )

    if not recomendaciones:
        recomendaciones.append(
            "Revisa en detalle cada criterio de evaluación e incorpora "
            "más términos específicos del dominio en tu entregable."
        )

    return Retroalimentacion(
        resumen=resumen,
        recomendaciones=recomendaciones,
        sin_mejoras_criticas=False,
    )


# ---------------------------------------------------------------------------
# Implementación principal
# ---------------------------------------------------------------------------

class HeuristicScoringEngine(ScoringEnginePort):
    """
    Motor de scoring determinista basado en keywords ponderadas.

    Implementa ScoringEnginePort. Se instancia sin estado compartido,
    por lo que es seguro reutilizarlo en múltiples peticiones.
    """

    def score(
        self,
        entregable: str,
        context: SimulationContext,
    ) -> SimulationResult:
        """
        Calcula el resultado de simulación completo en memoria (sin queries extra).

        Determinismo garantizado: dado el mismo entregable y context,
        siempre produce el mismo SimulationResult.
        """
        # ID determinista (UUID v5 basado en inputs)
        sim_seed = f"{context.tournament.id}:{context.team.id}:{entregable}"
        simulation_id = str(uuid.uuid5(_SIM_NS, sim_seed))

        # Precalcular tokens del entregable (una sola pasada)
        entregable_tokens = frozenset(_tokenize(entregable))
        base_q = _base_quality(entregable)

        # --- Score por criterio ---
        scores: List[CriterionScore] = []
        for criterio in context.criterios:
            kw_score = _criterion_keyword_score(
                entregable_tokens,
                criterio.name,
                criterio.description,
            )
            # Combinar calidad base (30%) + keywords del criterio (70%)
            combined = 0.30 * base_q + 0.70 * kw_score

            valor_simulado = _compute_valor_simulado(
                combined,
                criterio.min_qualification,
                criterio.max_qualification,
            )
            valor_normalizado = _compute_valor_normalizado(
                valor_simulado,
                criterio.min_qualification,
                criterio.max_qualification,
            )
            scores.append(
                CriterionScore(
                    criterio_id=criterio.id,
                    nombre=criterio.name,
                    peso=criterio.peso,
                    valor_simulado=valor_simulado,
                    valor_normalizado=valor_normalizado,
                    en_rango=(
                        criterio.min_qualification
                        <= valor_simulado
                        <= criterio.max_qualification
                    ),
                )
            )

        # --- puntaje_total (HU-SIM-02) ---
        puntaje_total = round(
            sum(s.valor_normalizado * s.peso / 100.0 for s in scores),
            2,
        )

        # --- Posición estimada (HU-SIM-03) ---
        posicion = _compute_posicion(
            puntaje_total,
            context.team.nivel_tecnico_declarado,
            context.total_approved_teams,
        )

        # --- Fortalezas y debilidades (HU-SIM-04) ---
        top_scores, bot_scores = _split_fortalezas_debilidades(scores)
        fortalezas = [
            _build_fortaleza_debilidad(s, is_weakness=False, min_q=0.0)
            for s in top_scores
        ]
        debilidades = [
            _build_fortaleza_debilidad(s, is_weakness=True, min_q=0.0)
            for s in bot_scores
        ]

        # --- Retroalimentación (HU-SIM-05) ---
        retro = _build_retroalimentacion(puntaje_total, posicion, debilidades, scores)

        return SimulationResult(
            simulation_id=simulation_id,
            scores=scores,
            puntaje_total=puntaje_total,
            posicion=posicion,
            fortalezas=fortalezas,
            debilidades=debilidades,
            retroalimentacion=retro,
        )
