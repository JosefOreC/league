from ....domain.ports.standing_repository import StandingRepository
from ....domain.entities.standing import Standing
from ...adapters.output.models import StandingModel, TournamentModel, TeamModel, GroupModel
from decimal import Decimal

class StandingRepositoryPostgresql(StandingRepository):
    
    @staticmethod
    def _standing_to_domain(standing_orm: StandingModel) -> Standing:
        standing = Standing(
            tournament_id=standing_orm.tournament_id,
            team_id=standing_orm.team_id,
            group_id=standing_orm.group_id
        )
        standing.update(
            win=False, # We don't have individual flags, but we have totals
            loss=False,
            draw=False,
            pts=0 # This update logic is a bit different from domain update()
        )
        # Direct assignment to private fields to reconstruct state
        standing._Standing__partidos_jugados = standing_orm.partidos_jugados
        standing._Standing__victorias = standing_orm.victorias
        standing._Standing__empates = standing_orm.empates
        standing._Standing__derrotas = standing_orm.derrotas
        standing._Standing__puntos = standing_orm.puntos
        standing._Standing__puntaje_favor = float(standing_orm.puntaje_favor)
        standing._Standing__puntaje_contra = float(standing_orm.puntaje_contra)
        standing._Standing__diferencia_puntaje = float(standing_orm.diferencia_puntaje)
        standing._Standing__posicion = standing_orm.posicion
        return standing

    def save(self, standing: Standing):
        tournament = TournamentModel.objects.get(pk=standing.tournament_id)
        team = TeamModel.objects.get(pk=standing.team_id)
        group = GroupModel.objects.get(pk=standing.group_id) if standing.group_id else None

        StandingModel.objects.update_or_create(
            tournament=tournament,
            team=team,
            defaults={
                "group": group,
                "partidos_jugados": standing.partidos_jugados,
                "victorias": standing.victorias,
                "empates": standing.empates,
                "derrotas": standing.derrotas,
                "puntos": standing.puntos,
                "puntaje_favor": Decimal(str(standing.puntaje_favor)),
                "puntaje_contra": Decimal(str(standing.puntaje_contra)),
                "diferencia_puntaje": Decimal(str(standing.diferencia_puntaje)),
                "posicion": standing.posicion
            }
        )

    def find_by_tournament(self, tournament_id: str) -> list[Standing]:
        standings_orm = StandingModel.objects.filter(tournament_id=tournament_id).order_by('posicion')
        return [self._standing_to_domain(s) for s in standings_orm]

    def find_by_group(self, group_id: str) -> list[Standing]:
        standings_orm = StandingModel.objects.filter(group_id=group_id).order_by('posicion')
        return [self._standing_to_domain(s) for s in standings_orm]

    def delete_by_tournament(self, tournament_id: str):
        StandingModel.objects.filter(tournament_id=tournament_id).delete()
