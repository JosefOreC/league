"""
Tests unitarios para CreateTournamentUseCase
"""
import unittest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from competencia.application.use_cases.create_tournament_use_case import CreateTournamentUseCase
from competencia.domain.ports.tournament_repository import TournamentRepository
from authentication.domain.entities.user import User
from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState
from competencia.domain.value_objects.enums.tournament_category import TournamentCategory


def _user(id=None, rol=SystemRol.MANAGER, state=UserState.ACTIVE) -> User:
    u_id = uuid.uuid4() if id is None else uuid.uuid5(uuid.NAMESPACE_DNS, str(id))
    return User(
        id=u_id, email=f"{id}@test.com", password_hash="hash",
        name=f"User {id}", rol=rol, state=state,
        birth_date=datetime(2005, 1, 1), attempts=0,
        blocked_until=None, created_at=datetime.now(),
        updated_at=datetime.now(), last_login=None
    )


class TestCreateTournamentUseCase(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=TournamentRepository)
        self.valid_name = "Torneo de Prueba"
        self.valid_desc = "Descripción del torneo"
        self.valid_start = datetime.now() + timedelta(days=10)
        self.valid_end = datetime.now() + timedelta(days=20)
        self.valid_category = TournamentCategory.CONSTRUCTOR
        self.valid_max_teams = 16

    def test_execute_ok_manager(self):
        user = _user(rol=SystemRol.MANAGER)
        use_case = CreateTournamentUseCase(user=user, tournament_repository=self.mock_repo)
        
        tournament = use_case.execute(
            name=self.valid_name,
            description=self.valid_desc,
            date_start=self.valid_start,
            date_end=self.valid_end,
            category=self.valid_category,
            max_teams=self.valid_max_teams
        )
        
        # Verificar que el torneo fue creado con los datos correctos
        self.assertIsNotNone(tournament)
        self.assertEqual(tournament.name, self.valid_name)
        self.assertEqual(tournament.description, self.valid_desc)
        self.assertEqual(tournament.creator_user_id, user.id)
        self.assertEqual(tournament.category, self.valid_category)
        self.assertEqual(tournament.tournament_rule.max_teams, self.valid_max_teams)
        
        # Verificar que el repositorio fue llamado con el torneo
        self.mock_repo.save.assert_called_once_with(tournament=tournament)

    def test_execute_ok_admin(self):
        user = _user(rol=SystemRol.ADMIN)
        use_case = CreateTournamentUseCase(user=user, tournament_repository=self.mock_repo)
        
        tournament = use_case.execute(
            name=self.valid_name,
            description=self.valid_desc,
            date_start=self.valid_start,
            date_end=self.valid_end,
            category=self.valid_category,
            max_teams=self.valid_max_teams
        )
        self.assertIsNotNone(tournament)
        self.mock_repo.save.assert_called_once()

    def test_execute_fails_if_user_not_manager_or_admin(self):
        user = _user(rol=SystemRol.PARTICIPANT)
        use_case = CreateTournamentUseCase(user=user, tournament_repository=self.mock_repo)
        
        with self.assertRaisesRegex(ValueError, "Sin permisos"):
            use_case.execute(
                name=self.valid_name, description=self.valid_desc,
                date_start=self.valid_start, date_end=self.valid_end,
                category=self.valid_category, max_teams=self.valid_max_teams
            )
            
        self.mock_repo.save.assert_not_called()

    def test_execute_fails_if_user_inactive(self):
        user = _user(rol=SystemRol.MANAGER, state=UserState.INACTIVE)
        use_case = CreateTournamentUseCase(user=user, tournament_repository=self.mock_repo)
        
        with self.assertRaisesRegex(ValueError, "Usuario inactivo"):
            use_case.execute(
                name=self.valid_name, description=self.valid_desc,
                date_start=self.valid_start, date_end=self.valid_end,
                category=self.valid_category, max_teams=self.valid_max_teams
            )
            
        self.mock_repo.save.assert_not_called()

    def test_execute_fails_if_invalid_dates(self):
        user = _user(rol=SystemRol.MANAGER)
        use_case = CreateTournamentUseCase(user=user, tournament_repository=self.mock_repo)
        
        # Fecha de fin antes de la de inicio
        with self.assertRaises(ValueError):
            use_case.execute(
                name=self.valid_name, description=self.valid_desc,
                date_start=self.valid_end, date_end=self.valid_start,
                category=self.valid_category, max_teams=self.valid_max_teams
            )
            
        self.mock_repo.save.assert_not_called()

if __name__ == "__main__":
    unittest.main()
