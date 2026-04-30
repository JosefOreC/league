import unittest
from unittest.mock import MagicMock
from competencia.application.use_cases.generate_fixtures_use_case import GenerateFixturesUseCase
from competencia.application.use_cases.calculate_standings_use_case import CalculateStandingsUseCase
from competencia.domain.entities.tournament import Tournament
from competencia.domain.entities.match import Match
from competencia.domain.value_objects.enums.tournament_state import TournamentState

class TestCompetenciaApplication(unittest.TestCase):
    def setUp(self):
        self.match_repo = MagicMock()
        self.tournament_repo = MagicMock()
        self.standing_repo = MagicMock()
        
        # Mocks para Use Cases
        self.generate_use_case = GenerateFixturesUseCase(self.match_repo, self.tournament_repo)
        self.standings_use_case = CalculateStandingsUseCase(self.match_repo, self.standing_repo)

    def test_generate_fixtures_calls_repos(self):
        # Setup mock tournament
        tournament_mock = MagicMock(spec=Tournament)
        tournament_mock.state = TournamentState.REGISTRATION_CLOSED
        tournament_mock.get_teams_accepted.return_value = [MagicMock(), MagicMock()]
        tournament_mock.config_tournament.NAME = "knockout"
        tournament_mock.id = "trn-1"
        
        self.tournament_repo.find_by_id.return_value = tournament_mock
        self.match_repo.find_by_tournament.return_value = []
        
        # Execute
        result = self.generate_use_case.execute("trn-1")
        
        # Verify
        self.tournament_repo.find_by_id.assert_called_with("trn-1")
        self.match_repo.delete_by_tournament.assert_called()
        self.match_repo.save.assert_called()
        tournament_mock.update_state.assert_called_with(TournamentState.IN_PROGRESS)

    def test_calculate_standings_logic(self):
        # Setup mock matches
        m1 = MagicMock(spec=Match)
        m1.estado = "FINISHED"
        m1.equipo_local_id = "t1"
        m1.equipo_visitante_id = "t2"
        m1.ganador_id = "t1"
        m1.es_bye = False
        m1.es_descanso = False
        m1.grupo_id = "g1"
        
        self.match_repo.find_by_tournament.return_value = [m1]
        
        # Execute
        result = self.standings_use_case.execute("trn-1")
        
        # Verify standings were saved
        self.standing_repo.delete_by_tournament.assert_called_with("trn-1")
        self.standing_repo.save.assert_called()
        
        # Check result data for t1 (winner)
        t1_standing = next(s for s in result if s["team_id"] == "t1")
        self.assertEqual(t1_standing["puntos"], 3)
        self.assertEqual(t1_standing["victorias"], 1)

if __name__ == "__main__":
    unittest.main()
