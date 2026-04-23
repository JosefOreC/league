"""
Tests unitarios para Team (domain/entities/team.py)
"""
import unittest
from datetime import datetime
from ..domain.entities.user import User
from ..domain.entities.team import Team
from ..domain.value_objects.enums.system_rol import SystemRol
from ..domain.value_objects.enums.user_state import UserState


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

def make_user(id="u-1", rol=SystemRol.PARTICIPANT, state=UserState.ACTIVE) -> User:
    return User(
        id=id, name=f"User {id}", email=f"{id}@test.com",
        date_registered=datetime(2024, 1, 1),
        birth_date=datetime(2005, 1, 1),
        rol=rol, state=state,
    )


def make_manager(id="mgr-1") -> User:
    return make_user(id=id, rol=SystemRol.MANAGER)


def make_coach(id="coach-1", state=UserState.ACTIVE) -> User:
    return make_user(id=id, rol=SystemRol.COACH, state=state)


def make_team(
    id="t-1",
    name="Equipo Alpha",
    members=None,
    leader=None,
) -> Team:
    manager = make_manager()
    coach   = make_coach()
    if members is None:
        members = [make_user("m-1")]
    return Team(
        id=id,
        name=name,
        creator_user=manager,
        teacher=coach,
        institution_id="inst-1",
        members=members,
        leader=leader,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTeamCreation(unittest.TestCase):

    def test_create_team_ok(self):
        team = make_team()
        self.assertEqual(team.id, "t-1")
        self.assertEqual(team.name, "Equipo Alpha")
        self.assertEqual(team.institution_id, "inst-1")
        self.assertEqual(len(team.members), 1)

    def test_name_too_short_raises(self):
        with self.assertRaises(ValueError):
            make_team(name="AB")

    def test_empty_institution_raises(self):
        manager = make_manager()
        coach   = make_coach()
        with self.assertRaises(ValueError):
            Team(id="t-1", name="Equipo", creator_user=manager,
                 teacher=coach, institution_id="", members=[make_user("m-1")])

    def test_creator_must_be_admin_or_manager(self):
        invalid_creator = make_user("bad", rol=SystemRol.PARTICIPANT)
        coach = make_coach()
        with self.assertRaises(ValueError):
            Team(id="t-1", name="Equipo", creator_user=invalid_creator,
                 teacher=coach, institution_id="inst-1", members=[make_user("m-1")])

    def test_teacher_must_be_coach(self):
        manager = make_manager()
        bad_teacher = make_user("bad", rol=SystemRol.PARTICIPANT)
        with self.assertRaises(ValueError):
            Team(id="t-1", name="Equipo", creator_user=manager,
                 teacher=bad_teacher, institution_id="inst-1", members=[make_user("m-1")])

    def test_teacher_must_be_active(self):
        manager = make_manager()
        inactive_coach = make_coach(state=UserState.INACTIVE)
        with self.assertRaises(ValueError):
            Team(id="t-1", name="Equipo", creator_user=manager,
                 teacher=inactive_coach, institution_id="inst-1", members=[make_user("m-1")])

    def test_no_members_raises(self):
        manager = make_manager()
        coach   = make_coach()
        with self.assertRaises(ValueError):
            Team(id="t-1", name="Equipo", creator_user=manager,
                 teacher=coach, institution_id="inst-1", members=[])


class TestTeamMembers(unittest.TestCase):

    def test_add_member_ok(self):
        team = make_team(members=[make_user("m-1")])
        team.add_member(make_user("m-2"))
        self.assertEqual(len(team.members), 2)

    def test_add_duplicate_member_raises(self):
        m1 = make_user("m-1")
        team = make_team(members=[m1])
        with self.assertRaises(ValueError):
            team.add_member(m1)

    def test_add_inactive_member_raises(self):
        team = make_team(members=[make_user("m-1")])
        inactive = make_user("m-2", state=UserState.INACTIVE)
        with self.assertRaises(ValueError):
            team.add_member(inactive)

    def test_add_non_participant_raises(self):
        team = make_team(members=[make_user("m-1")])
        admin = make_user("adm-2", rol=SystemRol.ADMIN)
        with self.assertRaises(ValueError):
            team.add_member(admin)

    def test_remove_member_ok(self):
        m1 = make_user("m-1")
        m2 = make_user("m-2")
        team = make_team(members=[m1, m2])
        team.remove_member(m2)
        self.assertEqual(len(team.members), 1)

    def test_remove_only_member_raises(self):
        m1 = make_user("m-1")
        team = make_team(members=[m1])
        with self.assertRaises(ValueError):
            team.remove_member(m1)

    def test_remove_nonexistent_member_raises(self):
        team = make_team(members=[make_user("m-1")])
        with self.assertRaises(ValueError):
            team.remove_member(make_user("no-existe"))


class TestTeamLeader(unittest.TestCase):

    def test_set_leader_ok(self):
        m1 = make_user("m-1")
        team = make_team(members=[m1])
        team.change_leader(m1)
        self.assertEqual(team.leader.id, "m-1")

    def test_leader_not_member_raises(self):
        team = make_team(members=[make_user("m-1")])
        outsider = make_user("m-99")
        with self.assertRaises(ValueError):
            team.change_leader(outsider)

    def test_leader_must_be_participant(self):
        coach = make_coach("m-1")  # rol=COACH, no es PARTICIPANT
        # no puede ser miembro para empezar, así que primero forzamos uno
        team = make_team(members=[make_user("m-1")])
        # intento de leader con rol incorrecto
        bad_leader = make_user("m-2", rol=SystemRol.COACH)
        with self.assertRaises(ValueError):
            team.change_leader(bad_leader)

    def test_has_leader_false_initially(self):
        team = make_team()
        self.assertFalse(team.has_leader())

    def test_has_leader_true_after_set(self):
        m1 = make_user("m-1")
        team = make_team(members=[m1])
        team.change_leader(m1)
        self.assertTrue(team.has_leader())

    def test_remove_leader_clears_leader(self):
        m1 = make_user("m-1")
        m2 = make_user("m-2")
        team = make_team(members=[m1, m2])
        team.change_leader(m1)
        team.remove_member(m1)
        self.assertIsNone(team.leader)


if __name__ == "__main__":
    unittest.main()
