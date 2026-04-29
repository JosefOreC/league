"""
Tests unitarios para User (domain/entities/user.py)
"""
import unittest
from datetime import datetime
from ..domain.entities.user import User
from ..domain.value_objects.enums.system_rol import SystemRol
from ..domain.value_objects.enums.user_state import UserState

# MOCKUP
def make_user(
    id="u-1",
    name="Juan Pérez",
    email="juan@test.com",
    rol=SystemRol.PARTICIPANT,
    state=UserState.ACTIVE,
    birth_date=datetime(2005, 6, 15),
) -> User:
    return User(
        id=id,
        name=name,
        email=email,
        date_registered=datetime(2024, 1, 1),
        birth_date=birth_date,
        rol=rol,
        state=state,
    )


class TestUserCreation(unittest.TestCase):

    def test_create_user_ok(self):
        user = make_user()
        self.assertEqual(user.id, "u-1")
        self.assertEqual(user.name, "Juan Pérez")
        self.assertEqual(user.email, "juan@test.com")
        self.assertEqual(user.rol, SystemRol.PARTICIPANT)
        self.assertEqual(user.state, UserState.ACTIVE)

    def test_age_is_calculated(self):
        birth = datetime(2000, 1, 1)
        user = make_user(birth_date=birth)
        expected_age = datetime.now().year - birth.year
        # ajuste si aún no cumplió años este año
        if datetime.now().month < birth.month or (
            datetime.now().month == birth.month and datetime.now().day < birth.day
        ):
            expected_age -= 1
        self.assertEqual(user.age, expected_age)


class TestUserRolState(unittest.TestCase):

    def test_admin_can_be_created(self):
        user = make_user(rol=SystemRol.ADMIN)
        self.assertEqual(user.rol, SystemRol.ADMIN)

    def test_coach_can_be_created(self):
        user = make_user(rol=SystemRol.COACH)
        self.assertEqual(user.rol, SystemRol.COACH)

    def test_manager_can_be_created(self):
        user = make_user(rol=SystemRol.MANAGER)
        self.assertEqual(user.rol, SystemRol.MANAGER)

    def test_active_user_can_participate(self):
        user = make_user(state=UserState.ACTIVE)
        self.assertTrue(user.can_participate())

    def test_inactive_user_cannot_participate(self):
        user = make_user(state=UserState.INACTIVE)
        self.assertFalse(user.can_participate())

    def test_banned_user_cannot_participate(self):
        user = make_user(state=UserState.BANNED)
        self.assertFalse(user.can_participate())


class TestUserPassword(unittest.TestCase):

    def test_set_and_verify_password(self):
        user = make_user()
        user.password = "Segura123"
        self.assertTrue(user.verify_password("Segura123"))

    def test_wrong_password_fails(self):
        user = make_user()
        user.password = "Segura123"
        self.assertFalse(user.verify_password("incorrecta"))

    def test_password_too_short_raises(self):
        user = make_user()
        with self.assertRaises(ValueError):
            user.password = "Ab1"

    def test_password_no_digit_raises(self):
        user = make_user()
        with self.assertRaises(ValueError):
            user.password = "SinNumero"

    def test_password_no_upper_raises(self):
        user = make_user()
        with self.assertRaises(ValueError):
            user.password = "sinmayuscula1"

    def test_password_getter_raises(self):
        user = make_user()
        with self.assertRaises(AttributeError):
            _ = user.password


if __name__ == "__main__":
    unittest.main()
