from ....domain.ports.final_ranking_repository import FinalRankingRepository
from ....domain.entities.final_ranking import FinalRanking
from ...adapters.output.models import FinalRankingModel, TournamentModel, TeamModel
from decimal import Decimal

class FinalRankingRepositoryPostgresql(FinalRankingRepository):
    
    @staticmethod
    def _ranking_to_domain(ranking_orm: FinalRankingModel) -> FinalRanking:
        return FinalRanking(
            tournament_id=ranking_orm.tournament_id,
            team_id=ranking_orm.team_id,
            posicion_final=ranking_orm.posicion_final,
            puntaje_total_acumulado=float(ranking_orm.puntaje_total_acumulado),
            medalla=ranking_orm.medalla,
            mencion_especial=ranking_orm.mencion_especial
        )

    def save(self, ranking: FinalRanking):
        tournament = TournamentModel.objects.get(pk=ranking.tournament_id)
        team = TeamModel.objects.get(pk=ranking.team_id)

        FinalRankingModel.objects.update_or_create(
            tournament=tournament,
            team=team,
            defaults={
                "posicion_final": ranking.posicion_final,
                "puntaje_total_acumulado": Decimal(str(ranking.puntaje_total_acumulado)),
                "medalla": ranking.medalla,
                "mencion_especial": ranking.mencion_especial
            }
        )

    def find_by_tournament(self, tournament_id: str) -> list[FinalRanking]:
        rankings_orm = FinalRankingModel.objects.filter(tournament_id=tournament_id).order_by('posicion_final')
        return [self._ranking_to_domain(r) for r in rankings_orm]

    def delete_by_tournament(self, tournament_id: str):
        FinalRankingModel.objects.filter(tournament_id=tournament_id).delete()
