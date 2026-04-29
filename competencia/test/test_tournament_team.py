"""
Tests unitarios para TournamentTeam (domain/entities/tournament_team.py)
"""
import unittest
from datetime import datetime
from ..domain.entities.user import User
from ..domain.entities.team import Team
from ..domain.entities.tournament_team import TournamentTeam
from ..domain.entities.tournament_rule import TournamentRule
from ..domain.entities.institution import Institution
from ..domain.value_objects.enums.system_rol import SystemRol
from ..domain.value_objects.enums.user_state import UserState
from ..domain.value_objects.enums.tournament_team_state import TournamentTeamState
from ..domain.value_objects.enums.tournament_access_type import TournamentAccessType
from ..domain.value_objects.enums.institution_category import InstitutionCategory


def _user(id="u-1", rol=SystemRol.PARTICIPANT, state=UserState.ACTIVE) -> User:
    return User(id=id, name=f"User {id}", email=f"{id}@test.com",
                date_registered=datetime(2024, 1, 1),
                birth_date=datetime(2005, 1, 1),
                rol=rol, state=state)

def _team(id="team-1", n_members=3) -> Team:
    manager = _user("mgr", rol=SystemRol.MANAGER)
    coach   = _user("coach", rol=SystemRol.COACH)
    members = [_user(f"m-{i}") for i in range(n_members)]
    # Set institution to string ID here as the team constructor expects string right now
    team = Team(id=id, name=f"Equipo {id}", creator_user=manager,
                teacher=coach, institution_id="inst-1", members=members)
    
    # We monkey patch the institution property for the test, 
    # since team.institution currently isn't implemented properly but TournamentTeam accesses it.
    inst = Institution(id=1, name="Inst", category=InstitutionCategory.PRIMARY, city="C", code="C")
    setattr(Team, "institution", property(lambda self: inst))
    
    return team

def _rule(min_members=2, max_members=5) -> TournamentRule:
    return TournamentRule.create(
        max_teams=8, min_members=min_members,
        max_members=max_members, min_teams=4,
        access_type=TournamentAccessType.PUBLIC,
    )

class TestTournamentTeam(unittest.TestCase):

    def test_create_tournament_team_ok(self):
        team = _team(n_members=3)
        rule = _rule(min_members=2, max_members=5)
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)
        
        self.assertEqual(tt.id, "tt-1")
        self.assertEqual(tt.tournament_id, 1)
        self.assertEqual(tt.state, TournamentTeamState.PENDING)
        self.assertEqual(tt.team.id, team.id)
        self.assertEqual(len(tt.members), 3)
        self.assertEqual(tt.teacher.id, "coach")
        self.assertEqual(tt.tournament_rule.id, rule.id)
        self.assertIsNotNone(tt.institution)
        self.assertIsNone(tt.leader)

    def test_create_fails_if_too_few_members(self):
        team = _team(n_members=1)
        rule = _rule(min_members=2, max_members=5)
        with self.assertRaises(ValueError):
            TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)

    def test_create_fails_if_too_many_members(self):
        team = _team(n_members=6)
        rule = _rule(min_members=2, max_members=5)
        with self.assertRaises(ValueError):
            TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)

    def test_set_state(self):
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=_rule(), state=TournamentTeamState.PENDING, team=_team(n_members=3))
        tt.state = TournamentTeamState.ACCEPTED
        self.assertEqual(tt.state, TournamentTeamState.ACCEPTED)

    def test_set_state_invalid_raises(self):
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=_rule(), state=TournamentTeamState.PENDING, team=_team(n_members=3))
        with self.assertRaises(ValueError):
            tt.state = "invalid"

    def test_add_member_ok(self):
        team = _team(n_members=3)
        rule = _rule(min_members=2, max_members=5)
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)
        
        new_member = _user("new-1")
        tt.add_member(new_member)
        self.assertEqual(len(tt.members), 4)

    def test_add_member_fails_if_exceeds_max(self):
        team = _team(n_members=5)
        rule = _rule(min_members=2, max_members=5)
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)
        
        new_member = _user("new-1")
        with self.assertRaises(ValueError):
            tt.add_member(new_member)

    def test_remove_member_ok(self):
        team = _team(n_members=3)
        rule = _rule(min_members=2, max_members=5)
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)
        
        member_to_remove = team.members[0]
        tt.remove_member(member_to_remove)
        self.assertEqual(len(tt.members), 2)

    def test_remove_member_fails_if_below_min(self):
        team = _team(n_members=2)
        rule = _rule(min_members=2, max_members=5)
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)
        
        member_to_remove = team.members[0]
        with self.assertRaises(ValueError):
            tt.remove_member(member_to_remove)

    def test_remove_member_removes_leader_if_is_leader(self):
        team = _team(n_members=3)
        leader = team.members[0]
        team.change_leader(leader)
        rule = _rule(min_members=2, max_members=5)
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)
        
        self.assertEqual(tt.leader.id, leader.id)
        tt.remove_member(leader)
        self.assertIsNone(tt.leader)

    def test_change_leader(self):
        team = _team(n_members=3)
        rule = _rule()
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)
        
        new_leader = team.members[1]
        tt.change_leader(new_leader)
        self.assertEqual(tt.leader.id, new_leader.id)

    def test_change_teacher(self):
        team = _team(n_members=3)
        rule = _rule()
        tt = TournamentTeam(id="tt-1", tournament_id=1, tournament_rule=rule, state=TournamentTeamState.PENDING, team=team)
        
        new_teacher = _user("coach-2", rol=SystemRol.COACH)
        tt.change_teacher(new_teacher)
        self.assertEqual(tt.teacher.id, new_teacher.id)

if __name__ == "__main__":
    unittest.main()
