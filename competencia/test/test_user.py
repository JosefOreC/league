"""
Tests unitarios para User (domain/entities/user.py)
"""
import unittest
from datetime import datetime
import uuid
from authentication.domain.entities.user import User
from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState

# MOCKUP
def make_user(
    id=None,
    name="Juan Pérez",
    email="juan@test.com",
    rol=SystemRol.PARTICIPANT,
    state=UserState.ACTIVE,
    birth_date=datetime(2005, 6, 15),
) -> User:
    if id is None:
        u_id = uuid.uuid4()
    elif isinstance(id, uuid.UUID):
        u_id = id
    else:
        u_id = uuid.uuid5(uuid.NAMESPACE_DNS, str(id))

    return User(
        id=u_id,
        email=email,
        password_hash="hash",
        name=name,
        rol=rol,
        state=state,
        birth_date=birth_date,
        attempts=0,
        blocked_until=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_login=None
    )


class TestUserCreation(unittest.TestCase):

    def test_create_user_ok(self):
        u_id = uuid.uuid4()
        user = make_user(id=u_id)
        self.assertEqual(user.id, u_id)
        self.assertEqual(user.name, "Juan Pérez")
        self.assertEqual(user.email, "juan@test.com")
        self.assertEqual(user.rol, SystemRol.PARTICIPANT)
        self.assertEqual(user.state, UserState.ACTIVE)

    def test_user_to_dict(self):
        user = make_user()
        d = user.to_external_dict()
        self.assertIn("id", d)
        self.assertEqual(d["name"], "Juan Pérez")
        self.assertEqual(d["rol"], "participant")

if __name__ == "__main__":
    unittest.main()
