from ...domain.ports.match_repository import MatchRepository
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.entities.match import Match
from ...domain.value_objects.enums.tournament_state import TournamentState
from ...domain.value_objects.enums.tournament_type import TournamentType
from uuid import uuid4
import math
import random

class GenerateFixturesUseCase:
    def __init__(self, match_repository: MatchRepository, tournament_repository: TournamentRepository):
        self.__match_repository = match_repository
        self.__tournament_repository = tournament_repository

    def execute(self, tournament_id: str):
        tournament = self.__tournament_repository.find_by_id(tournament_id)
        if not tournament:
            raise ValueError("Torneo no encontrado")
        
        # Validar estado para generar fixture
        if tournament.state != TournamentState.REGISTRATION_CLOSED:
             # Si está en REGISTRATION_OPEN, podríamos cerrarlo automáticamente si se solicita
             pass

        # Obtener equipos aprobados
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

        # Persistencia
        self.__match_repository.delete_by_tournament(tournament_id)
        for m in matches:
            self.__match_repository.save(m)
            
        # Transición de estado
        tournament.update_state(TournamentState.IN_PROGRESS)
        self.__tournament_repository.update(tournament)

        return [m.to_dict() for m in matches]

    def _generate_knockout(self, tournament_id, teams):
        n = len(teams)
        n_slots = 2**math.ceil(math.log2(n))
        n_byes = n_slots - n
        
        team_ids = [t.team.id for t in teams]
        random.shuffle(team_ids)
        
        # Slots filled with team_ids + Nones for byes
        # To avoid byes playing each other, we can place them strategically
        slots = team_ids + [None] * n_byes
        
        matches = []
        num_matches_round = n_slots // 2
        for i in range(num_matches_round):
            t1 = slots[i]
            t2 = slots[n_slots - 1 - i]
            
            is_bye = (t1 is None or t2 is None)
            match = Match(
                id=str(uuid4()),
                tournament_id=tournament_id,
                ronda=1,
                posicion_en_ronda=i + 1,
                equipo_local_id=t1 or t2, # If one is None, the other is local
                equipo_visitante_id=None if is_bye else t2,
                es_bye=is_bye,
                estado="FINISHED" if is_bye else "PENDING",
                ganador_id=t1 or t2 if is_bye else None,
                fase="KNOCKOUT"
            )
            matches.append(match)
        return matches

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
