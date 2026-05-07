from uuid import uuid4
from ...domain.ports.match_repository import MatchRepository
from ...domain.ports.match_result_repository import MatchResultRepository
from ...domain.ports.tournament_repository import TournamentRepository
from ...domain.ports.team_repository import TeamRepository
from ...domain.entities.match_result import MatchResult
from ...domain.entities.qualify_score_team import QualifyScoreTeam

class QualifyMatchUseCase:
    def __init__(self, 
                 match_repository: MatchRepository, 
                 match_result_repository: MatchResultRepository,
                 tournament_repository: TournamentRepository,
                 team_repository: TeamRepository):
        self.__match_repository = match_repository
        self.__match_result_repository = match_result_repository
        self.__tournament_repository = tournament_repository
        self.__team_repository = team_repository

    def execute(self, match_id: str, qualifications: list, user_id: str):
        match = self.__match_repository.find_by_id(match_id)
        if not match:
            raise ValueError("El partido no existe.")
        
        tournament = self.__tournament_repository.find_by_id(match.tournament_id)
        if not tournament:
            raise ValueError("El torneo asociado al partido no existe.")
        
        # Cargar equipos (TournamentTeam) en el agregado Tournament
        teams = self.__team_repository.find_by_tournament(tournament.id)
        tournament.set_teams(teams)
        
        evaluation = tournament.tournament_evaluation
        if not evaluation:
            raise ValueError("El torneo no tiene criterios de evaluación.")

        # 1. Calificar usando el dominio
        for qual in qualifications:
            team_id = qual['team_id']
            criterio_id = qual['criterio_id']
            value = float(qual['value'])
            
            # Buscar el TournamentTeam dentro del agregado Tournament
            t_team = tournament.search_team_by_id(team_id)
            
            # El encargado de calificar es TournamentEvaluation
            # Retorna un QualifyScoreTeam
            q_score = evaluation.qualify_score(t_team.team, criterio_id, value)
            
            # Se almacena en el TournamentTeam correspondiente
            t_team.add_qualify_score(q_score)

            # CALCULAR VALOR NORMALIZADO PARA PERSISTENCIA
            criterion = evaluation._find_criteria(criterio_id)
            # score_normalizado = (valor / max) * peso_criterio
            norm_value = value * criterion.value

            # Persistencia en MatchResult
            res = MatchResult(
                id=str(uuid4()),
                match_id=match_id,
                equipo_id=team_id,
                criterio_id=criterio_id,
                valor_registrado=value,
                valor_normalizado=norm_value,
                estado_resultado="DEFINITIVE",
                registrado_por=user_id
            )
            self.__match_result_repository.save(res)

        # 2. Persistir los cambios en el torneo/equipos
        # self.__tournament_repository.update(tournament) # ELIMINADO: Causaba borrado en cascada de resultados en el repo

        # 3. Determinar ganador usando lógica de dominio
        self._check_and_update_winner(match, tournament)

    def _check_and_update_winner(self, match, tournament):
        evaluation = tournament.tournament_evaluation
        
        # Recuperamos los TournamentTeam involucrados
        t_local = tournament.search_team_by_id(match.equipo_local_id)
        t_visitor = tournament.search_team_by_id(match.equipo_visitante_id)
        
        if not t_local or not t_visitor:
            return

        num_criterias = len(evaluation.criterias)
        
        if len(t_local.qualify_score_team) >= num_criterias and len(t_visitor.qualify_score_team) >= num_criterias:
            # El dominio calcula el puntaje pesado usando la lista de QualifyScoreTeam
            score_local = evaluation.get_qualify_weighted_score_team(t_local.qualify_score_team)
            score_visitor = evaluation.get_qualify_weighted_score_team(t_visitor.qualify_score_team)
            
            winner_id = match.equipo_local_id if score_local >= score_visitor else match.equipo_visitante_id
            
            match.set_winner(winner_id)
            self.__match_repository.save(match)
            
            if match.partido_siguiente_id:
                self._advance_winner(match)
            else:
                # Si no hay partido siguiente, es la FINAL. Finalizar torneo.
                tournament.finish_tournament()
                self.__tournament_repository.update_state(tournament)
                print(f"DEBUG: Torneo {tournament.id} FINALIZADO. Ganador: {match.ganador_id}")

    def _advance_winner(self, match):
        next_match = self.__match_repository.find_by_id(match.partido_siguiente_id)
        if not next_match: return
        
        if match.posicion_en_ronda % 2 != 0:
            next_match._Match__equipo_local_id = match.ganador_id
        else:
            next_match._Match__equipo_visitante_id = match.ganador_id
            
        self.__match_repository.save(next_match)
