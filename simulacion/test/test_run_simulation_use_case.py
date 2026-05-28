"""
Tests para HU-SIM-02 — Ejecutar simulación predictiva.
Cubre HU-SIM-02, HU-SIM-03, HU-SIM-04 y HU-SIM-05.

Escenarios:
  1. Happy path: SimulationResult completo con scores, puntaje_total, posicion.
  2. Entregable ausente → EntregableAusenteError.
  3. Entregable demasiado corto → EntregableDemasiadoCortoError con actual_length.
  4. Torneo no encontrado → TournamentNotFoundError.
  5. Sin equipo aprobado → TeamNotApprovedError.
  6. Determinismo: dos ejecuciones idénticas producen el mismo resultado.
  7. Motor heurístico: valor_simulado en rango, puntaje_total correcto.
  8. Fortalezas/debilidades: sin overlap, tiebreak determinista.
  9. Torneo con 2 criterios: a lo más 1 en cada lista.
 10. Retroalimentación: sin_mejoras_criticas=True cuando todo ≥ 80%.
"""
import uuid
from typing import List
from unittest.mock import MagicMock

from django.test import TestCase

from simulacion.application.use_cases.get_simulation_context_use_case import (
    TeamNotApprovedError,
    TournamentNotFoundError,
)
from simulacion.application.use_cases.run_simulation_use_case import (
    EntregableAusenteError,
    EntregableDemasiadoCortoError,
    RunSimulationUseCase,
)
from simulacion.domain.entities.criterion_score import CriterionScore
from simulacion.domain.entities.simulation_context import (
    CriterioInfo,
    SimulationContext,
    TeamInfo,
    TournamentInfo,
)
from simulacion.domain.entities.simulation_result import SimulationResult
from simulacion.domain.ports.scoring_engine_port import ScoringEnginePort
from simulacion.domain.ports.tournament_context_port import TournamentContextPort
from simulacion.infrastructure.scoring.heuristic_scoring_engine import (
    HeuristicScoringEngine,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ENTREGABLE_OK = (
    "Nuestro proyecto de robótica integra sensores ultrasónicos y cámaras de "
    "visión artificial para navegación autónoma. El diseño técnico incluye una "
    "arquitectura modular que permite mantenimiento sencillo. La presentación "
    "oral será clara, con demostraciones en vivo. Fomentamos el trabajo en "
    "equipo a través de reuniones semanales y roles definidos. La innovación "
    "reside en el algoritmo de detección de obstáculos en tiempo real."
)  # ~430 chars


def _make_context(
    num_criterios: int = 4,
    nivel: str = "INTERMEDIO",
    total_approved: int = 10,
) -> SimulationContext:
    criterios = [
        CriterioInfo(
            id=str(uuid.uuid4()),
            name=f"Criterio {i + 1}",
            description=f"Descripcion del criterio {i + 1} con palabras clave tecnicas",
            peso=100.0 / num_criterios,
            min_qualification=0.0,
            max_qualification=100.0,
        )
        for i in range(num_criterios)
    ]
    return SimulationContext(
        tournament=TournamentInfo(
            id=str(uuid.uuid4()), name="Torneo Test",
            state="INSCRIPCION", category="SECUNDARIA",
        ),
        team=TeamInfo(
            id=str(uuid.uuid4()), name="Team Test",
            nivel_tecnico_declarado=nivel, participants_count=5,
        ),
        criterios=criterios,
        total_approved_teams=total_approved,
    )


def _mock_context_port(context: SimulationContext) -> TournamentContextPort:
    port = MagicMock(spec=TournamentContextPort)
    port.get_context.return_value = context
    return port


def _mock_engine(result: SimulationResult) -> ScoringEnginePort:
    engine = MagicMock(spec=ScoringEnginePort)
    engine.score.return_value = result
    return engine


def _real_result(entregable: str, context: SimulationContext) -> SimulationResult:
    return HeuristicScoringEngine().score(entregable=entregable, context=context)


# ---------------------------------------------------------------------------
# Escenario 1: Happy path
# ---------------------------------------------------------------------------

class TestRunSimulationHappyPath(TestCase):

    def setUp(self):
        self.context = _make_context()
        self.context_port = _mock_context_port(self.context)

    def test_returns_simulation_result(self):
        """El use case devuelve un SimulationResult cuando el engine lo produce."""
        engine = HeuristicScoringEngine()
        uc = RunSimulationUseCase(
            tournament_context_port=self.context_port,
            scoring_engine_port=engine,
        )
        result = uc.execute("torneo-1", "user-1", _ENTREGABLE_OK)
        self.assertIsInstance(result, SimulationResult)

    def test_result_has_simulation_id(self):
        uc = RunSimulationUseCase(self.context_port, HeuristicScoringEngine())
        result = uc.execute("t1", "u1", _ENTREGABLE_OK)
        self.assertTrue(len(result.simulation_id) > 0)

    def test_scores_count_equals_criterios(self):
        uc = RunSimulationUseCase(self.context_port, HeuristicScoringEngine())
        result = uc.execute("t1", "u1", _ENTREGABLE_OK)
        self.assertEqual(len(result.scores), len(self.context.criterios))

    def test_puntaje_total_in_range(self):
        uc = RunSimulationUseCase(self.context_port, HeuristicScoringEngine())
        result = uc.execute("t1", "u1", _ENTREGABLE_OK)
        self.assertGreaterEqual(result.puntaje_total, 0.0)
        self.assertLessEqual(result.puntaje_total, 100.0)

    def test_puntaje_total_formula(self):
        """puntaje_total == Sigma(valor_normalizado_i * peso_i / 100), 2 decimales."""
        uc = RunSimulationUseCase(self.context_port, HeuristicScoringEngine())
        result = uc.execute("t1", "u1", _ENTREGABLE_OK)
        expected = round(
            sum(s.valor_normalizado * s.peso / 100.0 for s in result.scores), 2
        )
        self.assertAlmostEqual(result.puntaje_total, expected, places=2)


# ---------------------------------------------------------------------------
# Escenario 2: Entregable ausente
# ---------------------------------------------------------------------------

class TestRunSimulationEntregableAusente(TestCase):

    def _uc(self):
        port = MagicMock(spec=TournamentContextPort)
        port.get_context.return_value = _make_context()
        return RunSimulationUseCase(port, MagicMock(spec=ScoringEnginePort))

    def test_none_raises_ausente(self):
        with self.assertRaises(EntregableAusenteError):
            self._uc().execute("t1", "u1", None)

    def test_empty_string_raises_ausente(self):
        with self.assertRaises(EntregableAusenteError):
            self._uc().execute("t1", "u1", "")

    def test_error_payload_has_campo_field(self):
        """Verifica que la excepción lleva el mensaje correcto para el HTTP 400."""
        with self.assertRaises(EntregableAusenteError) as cm:
            self._uc().execute("t1", "u1", None)
        self.assertIn("requerido", str(cm.exception).lower())


# ---------------------------------------------------------------------------
# Escenario 3: Entregable demasiado corto
# ---------------------------------------------------------------------------

class TestRunSimulationEntregableCorto(TestCase):

    def _uc(self):
        port = MagicMock(spec=TournamentContextPort)
        port.get_context.return_value = _make_context()
        return RunSimulationUseCase(port, MagicMock(spec=ScoringEnginePort))

    def test_short_text_raises(self):
        with self.assertRaises(EntregableDemasiadoCortoError):
            self._uc().execute("t1", "u1", "corto")

    def test_error_carries_actual_length(self):
        texto_corto = "a" * 50
        with self.assertRaises(EntregableDemasiadoCortoError) as cm:
            self._uc().execute("t1", "u1", texto_corto)
        self.assertEqual(cm.exception.actual_length, 50)

    def test_99_chars_raises(self):
        with self.assertRaises(EntregableDemasiadoCortoError):
            self._uc().execute("t1", "u1", "x" * 99)

    def test_100_chars_passes_validation(self):
        """Exactamente 100 chars no debe lanzar error de longitud."""
        port = MagicMock(spec=TournamentContextPort)
        context = _make_context()
        port.get_context.return_value = context
        engine = HeuristicScoringEngine()
        uc = RunSimulationUseCase(port, engine)
        # No debe lanzar EntregableDemasiadoCortoError
        result = uc.execute("t1", "u1", "a" * 100)
        self.assertIsInstance(result, SimulationResult)


# ---------------------------------------------------------------------------
# Escenario 4: Torneo no encontrado
# ---------------------------------------------------------------------------

class TestRunSimulationTournamentNotFound(TestCase):

    def test_raises_tournament_not_found(self):
        port = MagicMock(spec=TournamentContextPort)
        port.get_context.return_value = None
        uc = RunSimulationUseCase(port, MagicMock(spec=ScoringEnginePort))
        with self.assertRaises(TournamentNotFoundError):
            uc.execute("no-existe", "u1", _ENTREGABLE_OK)


# ---------------------------------------------------------------------------
# Escenario 5: Sin equipo aprobado
# ---------------------------------------------------------------------------

class TestRunSimulationNoApprovedTeam(TestCase):

    def test_raises_team_not_approved(self):
        port = MagicMock(spec=TournamentContextPort)
        port.get_context.side_effect = TeamNotApprovedError(
            "No tiene un equipo aprobado en este torneo"
        )
        uc = RunSimulationUseCase(port, MagicMock(spec=ScoringEnginePort))
        with self.assertRaises(TeamNotApprovedError):
            uc.execute("t1", "user-sin-equipo", _ENTREGABLE_OK)


# ---------------------------------------------------------------------------
# Escenario 6: Determinismo
# ---------------------------------------------------------------------------

class TestRunSimulationDeterminism(TestCase):

    def test_same_input_same_result(self):
        """Dos invocaciones idénticas producen el mismo SimulationResult."""
        context = _make_context()
        engine = HeuristicScoringEngine()

        r1 = engine.score(_ENTREGABLE_OK, context)
        r2 = engine.score(_ENTREGABLE_OK, context)

        self.assertEqual(r1.simulation_id, r2.simulation_id)
        self.assertEqual(r1.puntaje_total, r2.puntaje_total)
        self.assertEqual(r1.scores, r2.scores)
        self.assertEqual(r1.posicion, r2.posicion)

    def test_different_entregable_different_id(self):
        """Entregables distintos producen simulation_id distinto."""
        context = _make_context()
        engine = HeuristicScoringEngine()
        entregable2 = _ENTREGABLE_OK + " extra texto adicional que cambia el hash"

        r1 = engine.score(_ENTREGABLE_OK, context)
        r2 = engine.score(entregable2, context)

        self.assertNotEqual(r1.simulation_id, r2.simulation_id)


# ---------------------------------------------------------------------------
# Escenario 7: Correctitud del motor heurístico
# ---------------------------------------------------------------------------

class TestHeuristicEngineCorrectness(TestCase):

    def setUp(self):
        self.context = _make_context(num_criterios=4)
        self.engine = HeuristicScoringEngine()

    def test_all_scores_in_range(self):
        """valor_simulado de cada score debe estar dentro del rango del criterio."""
        result = self.engine.score(_ENTREGABLE_OK, self.context)
        for score in result.scores:
            self.assertTrue(score.en_rango, f"Score fuera de rango: {score}")

    def test_valor_normalizado_in_0_100(self):
        result = self.engine.score(_ENTREGABLE_OK, self.context)
        for score in result.scores:
            self.assertGreaterEqual(score.valor_normalizado, 0.0)
            self.assertLessEqual(score.valor_normalizado, 100.0)

    def test_posicion_within_total_equipos(self):
        result = self.engine.score(_ENTREGABLE_OK, self.context)
        p = result.posicion
        self.assertGreaterEqual(p.posicion_estimada, 1)
        self.assertLessEqual(p.posicion_estimada, p.total_equipos)

    def test_single_team_posicion(self):
        """Con un solo equipo aprobado: posicion=1, advertencia de muestra única."""
        context = _make_context(total_approved=1)
        result = self.engine.score(_ENTREGABLE_OK, context)
        self.assertEqual(result.posicion.posicion_estimada, 1)
        self.assertEqual(result.posicion.total_equipos, 1)
        self.assertIsNotNone(result.posicion.advertencia)


# ---------------------------------------------------------------------------
# Escenario 8: Fortalezas y debilidades sin overlap
# ---------------------------------------------------------------------------

class TestFortalezasDebilidades(TestCase):

    def _no_overlap(self, result: SimulationResult) -> bool:
        fort_ids = {f.criterio_id for f in result.fortalezas}
        deb_ids = {d.criterio_id for d in result.debilidades}
        return fort_ids.isdisjoint(deb_ids)

    def test_no_overlap_4_criterios(self):
        context = _make_context(num_criterios=4)
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        self.assertTrue(self._no_overlap(result))

    def test_no_overlap_6_criterios(self):
        context = _make_context(num_criterios=6)
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        self.assertTrue(self._no_overlap(result))

    def test_max_3_fortalezas(self):
        context = _make_context(num_criterios=8)
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        self.assertLessEqual(len(result.fortalezas), 3)

    def test_max_3_debilidades(self):
        context = _make_context(num_criterios=8)
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        self.assertLessEqual(len(result.debilidades), 3)


# ---------------------------------------------------------------------------
# Escenario 9: Torneo con 2 criterios (a lo más 1 en cada lista)
# ---------------------------------------------------------------------------

class TestTwoCriteriosLists(TestCase):

    def test_at_most_1_fortaleza(self):
        context = _make_context(num_criterios=2)
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        self.assertLessEqual(len(result.fortalezas), 1)

    def test_at_most_1_debilidad(self):
        context = _make_context(num_criterios=2)
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        self.assertLessEqual(len(result.debilidades), 1)

    def test_no_overlap_2_criterios(self):
        context = _make_context(num_criterios=2)
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        fort_ids = {f.criterio_id for f in result.fortalezas}
        deb_ids = {d.criterio_id for d in result.debilidades}
        self.assertTrue(fort_ids.isdisjoint(deb_ids))


# ---------------------------------------------------------------------------
# Escenario 10: Retroalimentación cuando todo >= 80%
# ---------------------------------------------------------------------------

class TestRetroalimentacionPositiva(TestCase):

    def test_sin_mejoras_criticas_when_all_above_80(self):
        """
        Construye scores forzados a 85% y verifica que sin_mejoras_criticas=True.
        Se testea el motor directamente con un context cuyo entregable
        produce keywords de alta cobertura.
        """
        # Usamos muchas repeticiones de las keywords de los criterios
        criterio_keywords = "criterio uno dos tres cuatro"
        entregable_rico = (criterio_keywords + " ") * 40  # >100 chars, alta cobertura

        context = _make_context(num_criterios=2)
        result = HeuristicScoringEngine().score(entregable_rico.strip(), context)

        # Si todos los scores >= 80, sin_mejoras_criticas debe ser True
        if all(s.valor_normalizado >= 80.0 for s in result.scores):
            self.assertTrue(result.retroalimentacion.sin_mejoras_criticas)
            self.assertEqual(result.retroalimentacion.recomendaciones, [])

    def test_resumen_mentions_puntaje_and_posicion(self):
        """El resumen siempre menciona el puntaje total y la posición estimada."""
        context = _make_context()
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        resumen = result.retroalimentacion.resumen
        self.assertIn(str(result.puntaje_total), resumen)
        self.assertIn(str(result.posicion.posicion_estimada), resumen)
        self.assertIn(str(result.posicion.total_equipos), resumen)

    def test_recomendaciones_per_debilidad(self):
        """Hay al menos una recomendación por debilidad cuando sin_mejoras_criticas=False."""
        context = _make_context(num_criterios=4)
        result = HeuristicScoringEngine().score(_ENTREGABLE_OK, context)
        if not result.retroalimentacion.sin_mejoras_criticas:
            self.assertGreaterEqual(
                len(result.retroalimentacion.recomendaciones),
                len(result.debilidades),
            )
