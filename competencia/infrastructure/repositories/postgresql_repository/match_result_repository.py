from ....domain.ports.match_result_repository import MatchResultRepository
from ....domain.entities.match_result import MatchResult
from ...adapters.output.models import MatchResultModel, MatchModel, TeamModel, CriteriaModel
from decimal import Decimal

class MatchResultRepositoryPostgresql(MatchResultRepository):
    
    @staticmethod
    def _result_to_domain(result_orm: MatchResultModel) -> MatchResult:
        return MatchResult(
            id=result_orm.id,
            match_id=result_orm.match_id,
            equipo_id=result_orm.equipo_id,
            criterio_id=result_orm.criterio_id,
            valor_registrado=float(result_orm.valor_registrado),
            valor_normalizado=float(result_orm.valor_normalizado),
            estado_resultado=result_orm.estado_resultado,
            registrado_por=result_orm.registrado_por
        )

    def save(self, result: MatchResult):
        match_orm = MatchModel.objects.get(pk=result.match_id)
        team_orm = TeamModel.objects.get(pk=result.equipo_id)
        criteria_orm = CriteriaModel.objects.get(pk=result.criterio_id)

        try:
            MatchResultModel.objects.update_or_create(
                id=result.id,
                defaults={
                    "match": match_orm,
                    "equipo": team_orm,
                    "criterio": criteria_orm,
                    "valor_registrado": Decimal(str(result.valor_registrado)),
                    "valor_normalizado": Decimal(str(result.valor_normalizado)),
                    "estado_resultado": result.estado_resultado,
                    "registrado_por": result.registrado_por
                }
            )
        except Exception as e:
            raise e

    def find_by_match(self, match_id: str) -> list[MatchResult]:
        results_orm = MatchResultModel.objects.filter(match_id=match_id)
        return [self._result_to_domain(r) for r in results_orm]

    def find_by_team_in_match(self, team_id: str, match_id: str) -> list[MatchResult]:
        results_orm = MatchResultModel.objects.filter(match_id=match_id, equipo_id=team_id)
        return [self._result_to_domain(r) for r in results_orm]

    def find_by_tournament(self, tournament_id: str) -> list[MatchResult]:
        results_orm = MatchResultModel.objects.filter(match__tournament__id=tournament_id)
        return [self._result_to_domain(r) for r in results_orm]
