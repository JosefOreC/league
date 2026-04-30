"""
Tests unitarios para TournamentTeam (domain/entities/tournament_team.py)
"""
import unittest
import uuid
from datetime import datetime, timedelta
from authentication.domain.entities.user import User
from competencia.domain.entities.team import Team
from competencia.domain.entities.tournament_team import TournamentTeam
from competencia.domain.entities.participant import Participant
from competencia.domain.value_objects.enums.tournament_team_state import TournamentTeamState


from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState

def _user(id=None, rol=SystemRol.PARTICIPANT, state=UserState.ACTIVE) -> User:
    u_id = uuid.uuid4() if id is None else uuid.uuid5(uuid.NAMESPACE_DNS, str(id))
    return User(id=u_id, email=f"{id}@test.com", password_hash="hash",
                name=f"User {id}", rol=rol, state=state,
                birth_date=datetime(2005, 1, 1), attempts=0,
                blocked_until=None, created_at=datetime.now(),
                updated_at=datetime.now(), last_login=None)

def _participant(dni="12345678") -> Participant:
    return Participant(id=str(uuid.uuid4()), nombres="P", apellidos="L", documento_identidad=dni, autorizacion_datos=True)

def _team(id="team-1", n_participants=3) -> Team:
    participants = [_participant(dni=f"DNI-{i}") for i in range(n_participants)]
    return Team(
        id=id,
        tournament_id="trn-1",
        name=f"Equipo {id}",
        category="PRIMARY",
        institution_id="inst-1",
        nivel_tecnico_declarado="BASICO",
        representante_id="rep-1",
        docente_asesor_id="doc-1",
        participants=participants
    )

class TestTournamentTeam(unittest.TestCase):

    def test_create_tournament_team_ok(self):
        team = _team(n_participants=3)
        # Mock member_in_tournament_func
        member_check = lambda m_id: False
        
        tt = TournamentTeam(
            id="tt-1",
            tournament_id="trn-1",
            state=TournamentTeamState.PENDING,
            member_in_tournament_func=member_check,
            team=team,
            qualify_score_team=[]
        )
        
        self.assertEqual(tt.id, "tt-1")
        self.assertEqual(tt.tournament_id, "trn-1")
        self.assertEqual(tt.state, TournamentTeamState.PENDING)
        self.assertEqual(tt.team.id, team.id)
        self.assertEqual(len(tt.team.participants), 3)

    def test_set_state(self):
        team = _team()
        tt = TournamentTeam(id="tt-1", tournament_id="trn-1", state=TournamentTeamState.PENDING, 
                            member_in_tournament_func=lambda x: False, team=team, qualify_score_team=[])
        tt.state = TournamentTeamState.ACCEPTED
        self.assertEqual(tt.state, TournamentTeamState.ACCEPTED)

if __name__ == "__main__":
    unittest.main()
