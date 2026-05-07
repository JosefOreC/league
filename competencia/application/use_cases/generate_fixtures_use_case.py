from ...domain.ports.match_repository import MatchRepository
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.match import Match
from ...domain.value_objects.enums.tournament_state import TournamentState
from ...domain.value_objects.enums.tournament_type import TournamentType
from uuid import uuid4
import math
import random

from ...domain.ports.team_repository import TeamRepository

class GenerateFixturesUseCase:
    def __init__(self, match_repository: MatchRepository, tournament_repository: TournamentRepository, team_repository: TeamRepository):
        self.__match_repository = match_repository
        self.__tournament_repository = tournament_repository
        self.__team_repository = team_repository

    def execute(self, tournament_id: str):
        tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("Torneo no encontrado")
        
        if tournament.state != TournamentState.REGISTRATION_CLOSED:
             pass

        teams_from_db = self.__team_repository.find_by_tournament(tournament_id)
        tournament.set_teams(teams_from_db)

        teams = tournament.get_teams_accepted()
        if not teams:
            raise ValueError("No hay equipos aprobados para iniciar el torneo")

        matches = []
        if tournament.config_tournament.NAME == "knockout":
            matches = self._generate_knockout(tournament_id, teams)
        elif tournament.config_tournament.NAME == "round_robin":
            matches = self._generate_round_robin(tournament_id, teams)
        elif tournament.config_tournament.NAME == "hybrid":
            matches = self._generate_hybrid(tournament, teams)
        else:
            raise ValueError(f"Tipo de torneo no soportado")

        self.__match_repository.delete_by_tournament(tournament_id)
        for m in matches:
            self.__match_repository.save(m)
            
        self.__tournament_repository.update(tournament)

        return [m.to_dict() for m in matches]

    def _generate_knockout(self, tournament_id, teams):
        n = len(teams)
        if n < 2:
            raise ValueError("Se requieren al menos 2 equipos para generar llaves")
            
        n_slots = 2**math.ceil(math.log2(n))
        team_ids = [t.team.id for t in teams]
        random.shuffle(team_ids)
        
        # Rellenar con None para los Byes
        slots = team_ids + [None] * (n_slots - n)
        
        all_matches = []
        
        # Generar todos los partidos del árbol vacío primero para tener los IDs
        # Cantidad de rondas = log2(n_slots)
        num_rondas = int(math.log2(n_slots))
        
        rounds_matches = [] # List of lists of matches per round
        
        # 1. Crear estructura de partidos vacíos por ronda
        for r in range(1, num_rondas + 1):
            num_matches_in_round = n_slots // (2**r)
            round_list = []
            for i in range(num_matches_in_round):
                m = Match(
                    id=str(uuid4()),
                    tournament_id=tournament_id,
                    ronda=r,
                    posicion_en_ronda=i + 1,
                    estado="PENDING",
                    fase="KNOCKOUT"
                )
                round_list.append(m)
            rounds_matches.append(round_list)
            
        # 2. Vincular partidos con sus sucesores (partido_siguiente_id)
        for r in range(num_rondas - 1): # Todas las rondas menos la última (final)
            current_round = rounds_matches[r]
            next_round = rounds_matches[r+1]
            for i, match in enumerate(current_round):
                # El partido i y i+1 de la ronda r van al partido floor(i/2) de la ronda r+1
                match_siguiente = next_round[i // 2]
                # Hack para setear campo privado
                match._Match__partido_siguiente_id = match_siguiente.id
                
        # 3. Asignar equipos iniciales a la Ronda 1
        r1 = rounds_matches[0]
        for i in range(len(r1)):
            t1 = slots[i * 2]
            t2 = slots[i * 2 + 1]
            
            match = r1[i]
            match.set_teams(t1, t2)
            
            # Manejar BYES (si un equipo es None)
            if t1 is None or t2 is None:
                match._Match__es_bye = True
                match._Match__estado = "FINISHED"
                ganador = t1 or t2
                match._Match__ganador_id = ganador
                
                # Avanzar al ganador inmediatamente si no es la final
                if match.partido_siguiente_id:
                    self._advance_winner_to_next_match(match, rounds_matches)

        # Aplanar lista para retornar
        for r_list in rounds_matches:
            all_matches.extend(r_list)
            
        return all_matches

    def _advance_winner_to_next_match(self, match, rounds_matches):
        if not match.partido_siguiente_id: return
        
        # Buscar el partido siguiente en la estructura
        next_match = None
        for r_list in rounds_matches:
            for m in r_list:
                if m.id == match.partido_siguiente_id:
                    next_match = m
                    break
            if next_match: break
            
        if not next_match: return
        
        # Si la posición en ronda actual es impar (1, 3, 5...), va al local del siguiente
        # Si es par (2, 4, 6...), va al visitante
        if match.posicion_en_ronda % 2 != 0:
            next_match._Match__equipo_local_id = match.ganador_id
        else:
            next_match._Match__equipo_visitante_id = match.ganador_id

    def _generate_round_robin(self, tournament_id, teams):
        team_ids = [t.team.id for t in teams]
        if len(team_ids) % 2 != 0:
            team_ids.append(None)
            
        n = len(team_ids)
        rounds = n - 1
        matches = []
        
        for r in range(rounds):
            for i in range(n // 2):
                t1 = team_ids[i]
                t2 = team_ids[n - 1 - i]
                
                if t1 and t2:
                    match = Match(
                        id=str(uuid4()),
                        tournament_id=tournament_id,
                        ronda=r + 1,
                        posicion_en_ronda=i + 1,
                        equipo_local_id=t1,
                        equipo_visitante_id=t2,
                        fase="ROUND_ROBIN"
                    )
                    matches.append(match)
                elif t1 or t2:
                    match = Match(
                        id=str(uuid4()),
                        tournament_id=tournament_id,
                        ronda=r + 1,
                        posicion_en_ronda=i + 1,
                        equipo_local_id=t1 or t2,
                        equipo_visitante_id=None,
                        es_descanso=True,
                        estado="FINISHED",
                        fase="ROUND_ROBIN"
                    )
                    matches.append(match)
            team_ids = [team_ids[0]] + [team_ids[-1]] + team_ids[1:-1]
        return matches

    def _generate_hybrid(self, tournament, teams):
        # Hybrid usually has groups then knockout
        num_groups = getattr(tournament.config_tournament, 'num_groups', 2)
        
        # Serpentine distribution
        sorted_teams = sorted(teams, key=lambda x: x.team.name)
        groups = [[] for _ in range(num_groups)]
        for i, t in enumerate(sorted_teams):
            row = i // num_groups
            col = i % num_groups
            if row % 2 == 1:
                col = num_groups - 1 - col
            groups[col].append(t)
        
        all_matches = []
        # Generate Round Robin for each group
        for g_idx, g_teams in enumerate(groups):
            group_id = str(uuid4()) # In real app, create Group entity
            g_matches = self._generate_round_robin(tournament.id, g_teams)
            for m in g_matches:
                # Update phase and group_id
                # (Hackish way to set private fields for this demonstration)
                m._Match__fase = "GROUPS"
                m._Match__grupo_id = group_id
                all_matches.append(m)
        return all_matches
