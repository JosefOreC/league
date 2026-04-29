"""
Tests unitarios para Tournament y TournamentRule (domain/entities/)
"""
import unittest
from datetime import datetime, timedelta
from ..domain.entities.tournament import Tournament
from ..domain.entities.tournament_rule import TournamentRule
from ..domain.entities.user import User
from ..domain.entities.team import Team
from ..domain.value_objects.enums.tournament_state import TournamentState
from ..domain.value_objects.enums.tournament_category import TournamentCategory
from ..domain.value_objects.enums.tournament_access_type import TournamentAccessType
from ..domain.value_objects.enums.system_rol import SystemRol
from ..domain.value_objects.enums.user_state import UserState


# MOCKUP
def _user(id="u-1", rol=SystemRol.PARTICIPANT, state=UserState.ACTIVE) -> User:
    return User(id=id, name=f"User {id}", email=f"{id}@test.com",
                date_registered=datetime(2024, 1, 1),
                birth_date=datetime(2005, 1, 1),
                rol=rol, state=state)


def _manager(id="mgr-1") -> User:
    return _user(id=id, rol=SystemRol.MANAGER)


def _coach(id="coach-1") -> User:
    return _user(id=id, rol=SystemRol.COACH)


def _team(id="team-1", n_members=2, institution_id="inst-1") -> Team:
    manager = _manager()
    coach   = _coach()
    members = [_user(f"m-{i}") for i in range(n_members)]
    return Team(id=id, name=f"Equipo {id}", creator_user=manager,
                teacher=coach, institution_id=institution_id, members=members)


def _rule(min_members=2, max_members=5, min_teams=4, max_teams=16,
          access_type=TournamentAccessType.PUBLIC) -> TournamentRule:
    return TournamentRule.create(
        max_teams=max_teams, min_members=min_members,
        max_members=max_members, min_teams=min_teams,
        access_type=access_type,
    )


def _tournament(state=TournamentState.DRAFT, max_teams=8) -> Tournament:
    now = datetime.now()
    return Tournament(
        id="trn-1",
        name="Torneo Test",
        description="Descripción",
        date_start=now + timedelta(days=10),
        date_end=now + timedelta(days=40),
        tournament_rule=_rule(max_teams=max_teams),
        state=state,
        creator_user_id="mgr-1",
        category=TournamentCategory.EXPLORADOR,
    )


# ---------------------------------------------------------------------------
# TournamentRule Tests
# ---------------------------------------------------------------------------

class TestTournamentRuleCreation(unittest.TestCase):

    def test_create_rule_defaults(self):
        rule = _rule()
        self.assertEqual(rule.min_members, 2)
        self.assertEqual(rule.max_members, 5)
        self.assertEqual(rule.min_teams, 4)
        self.assertEqual(rule.max_teams, 16)

    def test_min_greater_than_max_members_raises(self):
        with self.assertRaises(ValueError):
            TournamentRule.create(max_teams=8, min_members=6, max_members=4)

    def test_max_members_less_than_2_raises(self):
        with self.assertRaises(ValueError):
            TournamentRule.create(max_teams=8, min_members=1, max_members=1)

    def test_min_greater_than_max_teams_raises(self):
        with self.assertRaises(ValueError):
            TournamentRule.create(max_teams=4, min_teams=8)

    def test_max_teams_less_than_4_raises(self):
        with self.assertRaises(ValueError):
            TournamentRule.create(max_teams=2)

    def test_max_teams_greater_than_64_raises(self):
        with self.assertRaises(ValueError):
            TournamentRule.create(max_teams=65)

    def test_id_is_generated(self):
        rule = _rule()
        self.assertIsNotNone(rule.id)
        self.assertIsInstance(rule.id, str)
        self.assertGreater(len(rule.id), 0)

    def test_access_type_default_is_private(self):
        rule = TournamentRule.create(max_teams=8)
        self.assertEqual(rule.access_type, TournamentAccessType.PRIVATE)

    def test_touch_updates_updated_at(self):
        rule = _rule()
        old_ts = rule.updated_at
        import time; time.sleep(0.01)
        rule.touch()
        self.assertGreater(rule.updated_at, old_ts)


class TestTournamentRuleValidation(unittest.TestCase):

    def test_validate_team_ok_public(self):
        rule = _rule(min_members=2, max_members=5, access_type=TournamentAccessType.PUBLIC)
        team = _team(n_members=3)
        self.assertTrue(rule.validate_team_rules(team))

    def test_validate_team_too_few_members(self):
        rule = _rule(min_members=3, max_members=5)
        team = _team(n_members=2)
        with self.assertRaises(ValueError):
            rule.validate_team_rules(team)

    def test_validate_team_too_many_members(self):
        rule = _rule(min_members=2, max_members=3)
        team = _team(n_members=4)
        with self.assertRaises(ValueError):
            rule.validate_team_rules(team)

    def test_validate_private_institution_not_in_list_raises(self):
        rule = TournamentRule.create(
            max_teams=8, access_type=TournamentAccessType.PRIVATE,
            validation_list=["inst-allowed"],
        )
        team = _team(institution_id="inst-NOT-allowed", n_members=2)
        with self.assertRaises(ValueError):
            rule.validate_team_rules(team)

    def test_validate_private_institution_in_list_ok(self):
        rule = TournamentRule.create(
            max_teams=8, access_type=TournamentAccessType.PRIVATE,
            validation_list=["inst-1"],
        )
        team = _team(institution_id="inst-1", n_members=2)
        self.assertTrue(rule.validate_team_rules(team))

    def test_validate_tournament_teams_ok(self):
        from competencia.domain.entities.tournament_team import TournamentTeam
        from competencia.domain.value_objects.enums.tournament_team_state import TournamentTeamState
        rule = _rule(min_teams=2, max_teams=8)
        t1 = TournamentTeam(id="tt-1", tournament_id="trn-1",
                            tournament_rule=rule, state=TournamentTeamState.PENDING,
                            team=_team("t-1", n_members=3))
        t2 = TournamentTeam(id="tt-2", tournament_id="trn-1",
                            tournament_rule=rule, state=TournamentTeamState.PENDING,
                            team=_team("t-2", n_members=3))
        self.assertTrue(rule.validate_tournament_teams([t1, t2]))

    def test_validate_tournament_teams_too_few(self):
        from competencia.domain.entities.tournament_team import TournamentTeam
        from competencia.domain.value_objects.enums.tournament_team_state import TournamentTeamState
        rule = _rule(min_teams=4, max_teams=8)
        t1 = TournamentTeam(id="tt-1", tournament_id="trn-1",
                            tournament_rule=rule, state=TournamentTeamState.PENDING,
                            team=_team("t-1", n_members=3))
        with self.assertRaises(ValueError):
            rule.validate_tournament_teams([t1])


# ---------------------------------------------------------------------------
# Tournament Tests
# ---------------------------------------------------------------------------

class TestTournamentCreate(unittest.TestCase):

    def test_create_factory_ok(self):
        now = datetime.now()
        t = Tournament.create(
            name="Copa 2026", description="Desc",
            date_start=now + timedelta(days=5),
            date_end=now + timedelta(days=30),
            max_teams=8, creator_user_id="mgr-1",
            category=TournamentCategory.CONSTRUCTOR,
        )
        self.assertEqual(t.name, "Copa 2026")
        self.assertEqual(t.state, TournamentState.DRAFT)
        self.assertEqual(t.category, TournamentCategory.CONSTRUCTOR)
        self.assertIsNotNone(t.id)

    def test_create_date_start_in_past_raises(self):
        now = datetime.now()
        with self.assertRaises(ValueError):
            Tournament.create(
                name="Copa", description="Desc",
                date_start=now - timedelta(days=1),
                date_end=now + timedelta(days=10),
                max_teams=8, creator_user_id="mgr-1",
                category=TournamentCategory.EXPLORADOR,
            )

    def test_create_date_end_before_start_raises(self):
        now = datetime.now()
        with self.assertRaises(ValueError):
            Tournament.create(
                name="Copa", description="Desc",
                date_start=now + timedelta(days=10),
                date_end=now + timedelta(days=5),
                max_teams=8, creator_user_id="mgr-1",
                category=TournamentCategory.EXPLORADOR,
            )


class TestTournamentStateTransitions(unittest.TestCase):

    def test_draft_to_in_review(self):
        t = _tournament(state=TournamentState.DRAFT)
        t.update_state(TournamentState.IN_REVIEW)
        self.assertEqual(t.state, TournamentState.IN_REVIEW)

    def test_in_review_to_draft(self):
        t = _tournament(state=TournamentState.IN_REVIEW)
        t.update_state(TournamentState.DRAFT)
        self.assertEqual(t.state, TournamentState.DRAFT)

    def test_in_review_to_registration_open(self):
        t = _tournament(state=TournamentState.IN_REVIEW)
        t.update_state(TournamentState.REGISTRATION_OPEN)
        self.assertEqual(t.state, TournamentState.REGISTRATION_OPEN)

    def test_invalid_transition_raises(self):
        t = _tournament(state=TournamentState.DRAFT)
        with self.assertRaises(ValueError):
            t.update_state(TournamentState.IN_PROGRESS)  # salto inválido

    def test_finalized_cannot_transition(self):
        t = _tournament(state=TournamentState.FINALIZED)
        with self.assertRaises(ValueError):
            t.update_state(TournamentState.IN_PROGRESS)


class TestTournamentTeamRegistration(unittest.TestCase):

    def _open_tournament(self, max_teams=8) -> Tournament:
        return _tournament(state=TournamentState.REGISTRATION_OPEN, max_teams=max_teams)

    def test_register_team_ok(self):
        t = self._open_tournament()
        team = _team(n_members=3)
        t.register_team(team)
        self.assertEqual(len(t.get_teams()), 1)

    def test_register_duplicate_team_raises(self):
        t = self._open_tournament()
        team = _team(n_members=3)
        t.register_team(team)
        with self.assertRaises(ValueError):
            t.register_team(team)

    def test_register_team_when_not_registration_open_raises(self):
        t = _tournament(state=TournamentState.DRAFT)
        with self.assertRaises(ValueError):
            t.register_team(_team(n_members=3))

    def test_unregister_team_ok(self):
        t = self._open_tournament()
        team = _team(n_members=3)
        t.register_team(team)
        t.unregister_team(team)
        self.assertEqual(len(t.get_teams()), 0)

    def test_tournament_is_full(self):
        t = self._open_tournament(max_teams=4)
        for i in range(4):
            t.register_team(_team(id=f"t-{i}", n_members=3))
        self.assertTrue(t.is_full())

    def test_register_beyond_max_raises(self):
        t = self._open_tournament(max_teams=4)
        for i in range(4):
            t.register_team(_team(id=f"t-{i}", n_members=3))
        with self.assertRaises(ValueError):
            t.register_team(_team(id="t-extra", n_members=3))


class TestTournamentQueries(unittest.TestCase):

    def test_contains_team_true(self):
        t = _tournament(state=TournamentState.REGISTRATION_OPEN)
        team = _team(n_members=3)
        t.register_team(team)
        self.assertTrue(t.contains_team(team))

    def test_contains_team_false(self):
        t = _tournament(state=TournamentState.REGISTRATION_OPEN)
        self.assertFalse(t.contains_team(_team(n_members=3)))

    def test_search_team_by_id_found(self):
        t = _tournament(state=TournamentState.REGISTRATION_OPEN)
        team = _team(id="specific-id", n_members=3)
        t.register_team(team)
        found = t.search_team_by_id("specific-id")
        self.assertEqual(found.team.id, "specific-id")

    def test_search_team_by_id_not_found_raises(self):
        t = _tournament(state=TournamentState.REGISTRATION_OPEN)
        with self.assertRaises(ValueError):
            t.search_team_by_id("no-existe")

    def test_get_teams_pending(self):
        t = _tournament(state=TournamentState.REGISTRATION_OPEN)
        t.register_team(_team(id="t-1", n_members=3))
        t.register_team(_team(id="t-2", n_members=3))
        self.assertEqual(len(t.get_teams_pending()), 2)


if __name__ == "__main__":
    unittest.main()
