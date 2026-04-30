import unittest
from datetime import datetime, timedelta
import uuid

# Mock ZoneInfo BEFORE importing User
from unittest.mock import MagicMock, patch
mock_zi = MagicMock()
# Devolvemos None para que datetime.now(None) funcione sin errores de tipo
with patch("zoneinfo.ZoneInfo", return_value=None):
    from authentication.domain.entities.user import User
    from authentication.domain.value_objects.enum.system_rol import SystemRol
    from authentication.domain.value_objects.enum.user_state import UserState
    from competencia.domain.entities.tournament_member import TournamentMember
from competencia.domain.value_objects.enums.tournament_rol import TournamentRol

class TestUserDomain(unittest.TestCase):
    def setUp(self):
        self.user_id = uuid.uuid4()
        # Usamos datetimes sin zona horaria para evitar dependencia de tzdata en tests locales
        self.birth_date = datetime(1995, 5, 15)
        self.user = User(
            id=self.user_id,
            email="atlet@test.com",
            password_hash="hashed_pw",
            name="Juan Perez",
            rol=SystemRol.PARTICIPANT,
            state=UserState.ACTIVE,
            birth_date=self.birth_date,
            attempts=0,
            blocked_until=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_login=None
        )

    def test_user_properties(self):
        self.assertEqual(self.user.name, "Juan Perez")
        self.assertEqual(self.user.email, "atlet@test.com")
        self.assertEqual(self.user.rol, SystemRol.PARTICIPANT)

    def test_invalid_email_setter(self):
        with self.assertRaises(ValueError):
            self.user.email = "invalid-email"
        with self.assertRaises(ValueError):
            self.user.email = "no-dot@domain"

    def test_password_validation(self):
        # Valid password
        self.assertTrue(self.user.verify_password_security("SafePass123"))
        
        # Invalid passwords
        with self.assertRaises(ValueError):
            self.user.verify_password_security("short1A")
        with self.assertRaises(ValueError):
            self.user.verify_password_security("nonumbersA")
        with self.assertRaises(ValueError):
            self.user.verify_password_security("NO_LOWER_CASE_1")

    @patch("zoneinfo.ZoneInfo", return_value=mock_zi)
    def test_account_locking(self, mock_tz):
        self.assertFalse(self.user.is_locked())
        # Simulate 5 failed attempts
        for i in range(5):
            self.user.increment_attempts()
        
        self.assertTrue(self.user.is_locked())
        self.assertEqual(self.user.state, UserState.BLOCKED)
        
        # Unlock
        self.user.unlock()
        self.assertFalse(self.user.is_locked())
        self.assertEqual(self.user.state, UserState.ACTIVE)
        self.assertEqual(self.user.attempts, 0)

    @patch("zoneinfo.ZoneInfo", return_value=mock_zi)
    def test_age_constraints(self, mock_tz):
        # Valid birth date
        valid_date = datetime.now() - timedelta(days=365*20)
        self.user.birth_date = valid_date
        
        # Too old
        too_old = datetime.now() - timedelta(days=365*90)
        with self.assertRaises(ValueError):
            self.user.birth_date = too_old
            
        # Too young
        too_young = datetime.now() - timedelta(days=365*1)
        with self.assertRaises(ValueError):
            self.user.birth_date = too_young

if __name__ == "__main__":
    unittest.main()
