import unittest
from datetime import datetime, timedelta
from competencia.domain.entities.tournament import Tournament
from competencia.domain.entities.team import Team
from competencia.domain.entities.participant import Participant
from competencia.domain.value_objects.enums.tournament_state import TournamentState
from competencia.domain.value_objects.enums.tournament_category import TournamentCategory
from competencia.domain.value_objects.enums.tournament_team_state import TournamentTeamState
from competencia.domain.entities.tournament_rule import TournamentRule
from competencia.domain.value_objects.enums.tournament_access_type import TournamentAccessType
from competencia.domain.entities.tournament_member import TournamentMember
from competencia.domain.value_objects.enums.tournament_rol import TournamentRol

class TestTournamentDomainLogic(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now()
        # Creamos una regla publica para evitar validaciones de institucion en este test
        rule = TournamentRule.create(
            max_teams=4, access_type=TournamentAccessType.PUBLIC,
            date_start_inscription=self.now + timedelta(days=1),
            date_end_inscription=self.now + timedelta(days=20)
        )
        # Miembros obligatorios
        members = [TournamentMember(user_id="admin-id", tournament_id="trn-1", rol=TournamentRol.MANAGER)]
        # Creamos un torneo base
        self.tournament = Tournament(
            id="trn-1",
            name="Olimpiada de Ciencias",
            description="Torneo nacional",
            date_start=self.now + timedelta(days=30),
            date_end=self.now + timedelta(days=60),
            tournament_rule=rule,
            state=TournamentState.DRAFT,
            creator_user_id="admin-id",
            category=TournamentCategory.EXPLORADOR,
            users_tournaments=members
        )
        # Forzamos estado a REGISTRATION_OPEN para pruebas de inscripción
        self.tournament.update_state(TournamentState.IN_REVIEW)
        self.tournament.update_state(TournamentState.REGISTRATION_OPEN)

    def test_add_team_with_duplicate_participant_dni(self):
        # Equipo 1 con Participante A y B (min 2)
        p_a = Participant(id="p1", nombres="Carlos", apellidos="Ruiz", documento_identidad="77889900")
        p_b = Participant(id="p2", nombres="Ana", apellidos="Guerra", documento_identidad="11223344")
        team1 = Team(id="t1", tournament_id=self.tournament.id, name="Team Alpha", 
                     category="PRIMARY", institution_id="inst-1", 
                     nivel_tecnico_declarado="BASICO", representante_id="rep-1", 
                     docente_asesor_id="doc-1", participants=[p_a, p_b])
        
        self.tournament.add_team(team1)
        
        # Equipo 2 con el MISMO Participante A (mismo DNI)
        p_a_duplicate = Participant(id="p3", nombres="Carlos", apellidos="Ruiz", documento_identidad="77889900")
        p_c = Participant(id="p4", nombres="Luis", apellidos="Paz", documento_identidad="55667788")
        team2 = Team(id="t2", tournament_id=self.tournament.id, name="Team Beta", 
                     category="PRIMARY", institution_id="inst-1", 
                     nivel_tecnico_declarado="BASICO", representante_id="rep-2", 
                     docente_asesor_id="doc-2", participants=[p_a_duplicate, p_c])
        
        with self.assertRaises(ValueError) as context:
            self.tournament.add_team(team2)
        
        self.assertIn("ya está inscrito en este torneo", str(context.exception))

    def test_tournament_full_capacity(self):
        # Llenar el torneo (max_teams=4)
        for i in range(4):
            p1 = Participant(id=f"p1_{i}", nombres=f"U1_{i}", apellidos="Test", documento_identidad=f"DNI1_{i}")
            p2 = Participant(id=f"p2_{i}", nombres=f"U2_{i}", apellidos="Test", documento_identidad=f"DNI2_{i}")
            team = Team(id=f"t{i}", tournament_id=self.tournament.id, name=f"Team{i}", 
                         category="PRIMARY", institution_id="inst-1", 
                         nivel_tecnico_declarado="BASICO", representante_id=f"rep{i}", 
                         docente_asesor_id="doc-1", participants=[p1, p2])
            
            self.tournament.add_team(team)
            self.tournament.get_teams()[i].state = TournamentTeamState.ACCEPTED
            
        # Intentar agregar el 5to
        p_e1 = Participant(id="pe1", nombres="E1", apellidos="U", documento_identidad="DE1")
        p_e2 = Participant(id="pe2", nombres="E2", apellidos="U", documento_identidad="DE2")
        team_extra = Team(id="textra", tournament_id=self.tournament.id, name="Extra Team", 
                           category="PRIMARY", institution_id="inst-1", 
                           nivel_tecnico_declarado="BASICO", representante_id="rep-e", 
                           docente_asesor_id="doc-1", participants=[p_e1, p_e2])
        
        with self.assertRaises(ValueError) as context:
            self.tournament.add_team(team_extra)
        
        self.assertIn("ha alcanzado el número máximo", str(context.exception))

    def test_state_transition_validation(self):
        # De REGISTRATION_OPEN no puede saltar directamente a FINALIZED
        with self.assertRaises(ValueError):
            self.tournament.update_state(TournamentState.FINALIZED)
            
        self.tournament.update_state(TournamentState.REGISTRATION_CLOSED)
        self.assertEqual(self.tournament.state, TournamentState.REGISTRATION_CLOSED)

if __name__ == "__main__":
    unittest.main()
