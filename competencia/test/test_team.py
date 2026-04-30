"""
Tests unitarios para Team (domain/entities/team.py)
"""
import unittest
import uuid
from datetime import datetime
from competencia.domain.entities.team import Team
from competencia.domain.entities.participant import Participant


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

def make_participant(id=None, dni="12345678") -> Participant:
    p_id = str(uuid.uuid4()) if id is None else str(id)
    return Participant(
        id=p_id,
        nombres="P-Name",
        apellidos="P-LastName",
        documento_identidad=dni,
        autorizacion_datos=True
    )


def make_team(
    id="t-1",
    tournament_id="trn-1",
    name="Equipo Alpha",
    participants=None,
) -> Team:
    if participants is None:
        participants = [make_participant(dni="00000001")]
    
    return Team(
        id=id,
        tournament_id=tournament_id,
        name=name,
        category="PRIMARY",
        institution_id="inst-1",
        nivel_tecnico_declarado="BASICO",
        representante_id="rep-1",
        docente_asesor_id="doc-1",
        participants=participants
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
        self.assertEqual(len(team.participants), 1)

class TestTeamParticipants(unittest.TestCase):

    def test_add_participant_ok(self):
        team = make_team(participants=[make_participant(dni="1")])
        p2 = make_participant(dni="2")
        team.add_participant(p2)
        self.assertEqual(len(team.participants), 2)
        self.assertEqual(team.participants[1].documento_identidad, "2")

class TestTeamState(unittest.TestCase):

    def test_approve_team(self):
        team = make_team()
        self.assertEqual(team.estado_inscripcion, "PENDIENTE")
        team.approve()
        self.assertEqual(team.estado_inscripcion, "APROBADO")

    def test_reject_team(self):
        team = make_team()
        team.reject()
        self.assertEqual(team.estado_inscripcion, "RECHAZADO")

if __name__ == "__main__":
    unittest.main()
