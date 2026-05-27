"""
Tests para HU-SIM-01 — Obtener contexto de simulación del torneo.

Cubre los 5 escenarios de aceptación:
  1. Happy path: contexto devuelto correctamente con port mockeado.
  2. 403: representante sin equipo aprobado en el torneo.
  3. 404: torneo no encontrado.
  4. assertNumQueries(<=3): repositorio real con fixtures mínimos en memoria.
  5. Determinismo: misma entrada → mismo SimulationContext.

Arquitectura de tests:
  - Tests unitarios del caso de uso (con port mockeado via unittest.mock).
  - Test de integración del repositorio real (TransactionTestCase) que verifica
    que la consulta optimizada no supera 3 queries SQL.
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock

from django.test import TestCase, TransactionTestCase

from simulacion.application.use_cases.get_simulation_context_use_case import (
    GetSimulationContextUseCase,
    TeamNotApprovedError,
    TournamentNotFoundError,
)
from simulacion.domain.entities.simulation_context import (
    CriterioInfo,
    SimulationContext,
    TeamInfo,
    TournamentInfo,
)
from simulacion.domain.ports.tournament_context_port import TournamentContextPort


# ---------------------------------------------------------------------------
# Helpers: builders de datos de prueba
# ---------------------------------------------------------------------------

def _make_tournament_info(**overrides) -> TournamentInfo:
    defaults = dict(
        id=str(uuid.uuid4()),
        name='Torneo de Robótica 2026',
        state='INSCRIPCION',
        category='SECUNDARIA',
    )
    defaults.update(overrides)
    return TournamentInfo(**defaults)


def _make_team_info(**overrides) -> TeamInfo:
    defaults = dict(
        id=str(uuid.uuid4()),
        name='Team Alpha',
        nivel_tecnico_declarado='INTERMEDIO',
        participants_count=5,
    )
    defaults.update(overrides)
    return TeamInfo(**defaults)


def _make_criterio(**overrides) -> CriterioInfo:
    defaults = dict(
        id=str(uuid.uuid4()),
        name='Diseño técnico',
        description='Calidad del diseño técnico del prototipo',
        peso=25.0,
        min_qualification=0.0,
        max_qualification=100.0,
    )
    defaults.update(overrides)
    return CriterioInfo(**defaults)


def _make_context() -> SimulationContext:
    """Crea un SimulationContext completo con 4 criterios que suman 100%."""
    criterios = [
        _make_criterio(name='Diseño técnico', peso=30.0),
        _make_criterio(name='Innovación', peso=25.0),
        _make_criterio(name='Presentación oral', peso=25.0),
        _make_criterio(name='Trabajo en equipo', peso=20.0),
    ]
    return SimulationContext(
        tournament=_make_tournament_info(),
        team=_make_team_info(),
        criterios=criterios,
    )


# ---------------------------------------------------------------------------
# Escenario 1: Happy path con port mockeado
# ---------------------------------------------------------------------------

class TestGetSimulationContextHappyPath(TestCase):

    def setUp(self):
        self.mock_port: TournamentContextPort = MagicMock(spec=TournamentContextPort)
        self.use_case = GetSimulationContextUseCase(tournament_context_port=self.mock_port)

    def test_returns_simulation_context(self):
        """El use case devuelve el SimulationContext cuando el port lo retorna."""
        expected_context = _make_context()
        self.mock_port.get_context.return_value = expected_context

        result = self.use_case.execute(
            tournament_id='torneo-uuid-123',
            representante_id='user-uuid-456',
        )

        self.assertEqual(result, expected_context)
        self.mock_port.get_context.assert_called_once_with(
            tournament_id='torneo-uuid-123',
            representante_id='user-uuid-456',
        )

    def test_context_has_tournament_team_and_criterios(self):
        """El SimulationContext contiene los tres sub-objetos esperados."""
        expected_context = _make_context()
        self.mock_port.get_context.return_value = expected_context

        result = self.use_case.execute('t1', 'u1')

        self.assertIsInstance(result.tournament, TournamentInfo)
        self.assertIsInstance(result.team, TeamInfo)
        self.assertEqual(len(result.criterios), 4)
        self.assertIsInstance(result.criterios[0], CriterioInfo)

    def test_criterios_sum_to_100(self):
        """La suma de pesos de los criterios del torneo es 100%."""
        expected_context = _make_context()
        self.mock_port.get_context.return_value = expected_context

        result = self.use_case.execute('t1', 'u1')

        total_peso = sum(c.peso for c in result.criterios)
        self.assertAlmostEqual(total_peso, 100.0, places=1)


# ---------------------------------------------------------------------------
# Escenario 2: 403 — representante sin equipo aprobado
# ---------------------------------------------------------------------------

class TestGetSimulationContextNoApprovedTeam(TestCase):

    def setUp(self):
        self.mock_port: TournamentContextPort = MagicMock(spec=TournamentContextPort)
        self.use_case = GetSimulationContextUseCase(tournament_context_port=self.mock_port)

    def test_raises_team_not_approved_error(self):
        """
        El use case propaga TeamNotApprovedError cuando el port la lanza.
        Esto corresponde al HTTP 403 en la vista.
        """
        self.mock_port.get_context.side_effect = TeamNotApprovedError(
            "No tiene un equipo aprobado en este torneo"
        )

        with self.assertRaises(TeamNotApprovedError):
            self.use_case.execute(
                tournament_id='torneo-uuid-123',
                representante_id='usuario-sin-equipo',
            )

    def test_error_message_content(self):
        """El mensaje de TeamNotApprovedError contiene el texto esperado."""
        self.mock_port.get_context.side_effect = TeamNotApprovedError(
            "No tiene un equipo aprobado en este torneo"
        )

        with self.assertRaises(TeamNotApprovedError) as cm:
            self.use_case.execute('t1', 'u-no-team')

        self.assertIn('equipo aprobado', str(cm.exception))


# ---------------------------------------------------------------------------
# Escenario 3: 404 — torneo no encontrado
# ---------------------------------------------------------------------------

class TestGetSimulationContextTournamentNotFound(TestCase):

    def setUp(self):
        self.mock_port: TournamentContextPort = MagicMock(spec=TournamentContextPort)
        self.use_case = GetSimulationContextUseCase(tournament_context_port=self.mock_port)

    def test_raises_tournament_not_found_when_port_returns_none(self):
        """
        El use case lanza TournamentNotFoundError cuando el port devuelve None.
        Esto corresponde al HTTP 404 en la vista.
        """
        self.mock_port.get_context.return_value = None

        with self.assertRaises(TournamentNotFoundError):
            self.use_case.execute(
                tournament_id='id-que-no-existe',
                representante_id='cualquier-user',
            )

    def test_error_message_includes_tournament_id(self):
        """El mensaje de TournamentNotFoundError incluye el tournament_id buscado."""
        self.mock_port.get_context.return_value = None

        with self.assertRaises(TournamentNotFoundError) as cm:
            self.use_case.execute('id-que-no-existe', 'u1')

        self.assertIn('id-que-no-existe', str(cm.exception))


# ---------------------------------------------------------------------------
# Escenario 4: assertNumQueries(<=3) — repositorio real
# ---------------------------------------------------------------------------

class TestTournamentContextRepositoryNumQueries(TransactionTestCase):
    """
    Test de integración que verifica que el repositorio real (con base de datos)
    no supera 3 queries SQL al obtener el contexto de simulación.

    PREREQUISITO: La base de datos de test debe estar configurada y accesible.
    Se usan los modelos reales de competencia/ sin fixtures de archivo.
    """

    def _create_test_data(self):
        """Crea datos mínimos en la DB de test para verificar el número de queries."""
        from competencia.infrastructure.adapters.output.models import (
            CriteriaModel,
            DocenteAsesorModel,
            InstitutionModel,
            ParticipantModel,
            TeamModel,
            TournamentModel,
            TournamentRuleModel,
        )

        now = datetime(2026, 1, 1, 0, 0)
        rule = TournamentRuleModel.objects.create(
            id=str(uuid.uuid4()),
            min_members=3, max_members=6,
            min_teams=2, max_teams=16,
            access_type='ABIERTO',
            created_at=now, updated_at=now,
        )
        tournament = TournamentModel.objects.create(
            id=str(uuid.uuid4()),
            name='Torneo Test NumQueries',
            description='Test',
            date_start=now, date_end=now,
            state='INSCRIPCION',
            category='SECUNDARIA',
            creator_user_id=str(uuid.uuid4()),
            tournament_rule=rule,
            config_tournament={},
        )
        for i in range(8):
            CriteriaModel.objects.create(
                id=str(uuid.uuid4()),
                name=f'Criterio {i + 1:02d}',
                description=f'Descripción del criterio {i + 1}',
                value=12.5,
                min_value_qualification=0.0,
                max_value_qualification=100.0,
                created_at=now, updated_at=now,
                tournament=tournament,
            )

        institution = InstitutionModel.objects.create(
            id=str(uuid.uuid4()),
            name='IES Test', type='PUBLICA',
            city='Lima', country='PE',
        )
        docente = DocenteAsesorModel.objects.create(
            id=str(uuid.uuid4()),
            nombre_completo='Docente Test',
            email='docente@test.com',
            telefono='999999999',
            institution=institution,
        )
        representante_id = str(uuid.uuid4())
        team = TeamModel.objects.create(
            id=str(uuid.uuid4()),
            tournament=tournament,
            name='Team NumQueries',
            category='SECUNDARIA',
            institution=institution,
            nivel_tecnico_declarado='AVANZADO',
            estado_inscripcion='APROBADO',
            representante_id=representante_id,
            docente_asesor=docente,
        )
        for j in range(5):
            ParticipantModel.objects.create(
                id=str(uuid.uuid4()),
                team=team,
                nombres=f'Participante{j}',
                apellidos='Test',
                edad=16,
                grado_academico='5to Secundaria',
                documento_identidad=f'7000000{j}',
                autorizacion_datos=True,
            )

        return tournament.id, representante_id

    def test_repository_uses_at_most_3_queries(self):
        """
        Escenario: assertNumQueries(<=3) — 1 query principal + 2 prefetches.
        Con un torneo que tiene 8 criterios y un equipo con 5 participantes.
        """
        from simulacion.infrastructure.repositories.tournament_context_repository import (
            TournamentContextRepository,
        )

        tournament_id, representante_id = self._create_test_data()
        repo = TournamentContextRepository()

        with self.assertNumQueries(3):
            context = repo.get_context(
                tournament_id=str(tournament_id),
                representante_id=representante_id,
            )

        # Verificaciones adicionales de correctitud
        self.assertIsNotNone(context)
        self.assertEqual(len(context.criterios), 8)
        self.assertEqual(context.team.participants_count, 5)
        self.assertEqual(context.team.nivel_tecnico_declarado, 'AVANZADO')


# ---------------------------------------------------------------------------
# Escenario 5: Determinismo — misma entrada → mismo resultado
# ---------------------------------------------------------------------------

class TestGetSimulationContextDeterminism(TestCase):

    def test_same_input_returns_equal_context(self):
        """
        El SimulationContext es un frozen dataclass: dos ejecuciones con el mismo
        port que devuelve el mismo objeto producen resultados iguales.
        """
        mock_port: TournamentContextPort = MagicMock(spec=TournamentContextPort)
        context = _make_context()
        mock_port.get_context.return_value = context

        use_case = GetSimulationContextUseCase(tournament_context_port=mock_port)

        result_1 = use_case.execute('t1', 'u1')
        # Reseteamos el mock para simular segunda llamada independiente
        mock_port.get_context.return_value = context
        result_2 = use_case.execute('t1', 'u1')

        self.assertEqual(result_1, result_2)
        self.assertEqual(result_1.criterios, result_2.criterios)
