from ....domain.ports.tournament_repository import TournamentRepository
from ....domain.entities.tournament import Tournament
from ....domain.entities.tournament_rule import TournamentRule
from ....domain.value_objects.enums.tournament_state import TournamentState
from ....domain.value_objects.enums.tournament_access_type import TournamentAccessType
from ....domain.value_objects.enums.tournament_category import TournamentCategory
from ...adapters.output.models import TournamentModel, TournamentRuleModel


class TournamentRepositoryPostgresql(TournamentRepository):

    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # MAPPERS
    # -------------------------------------------------------------------------

    @staticmethod
    def _rule_to_domain(rule_orm: TournamentRuleModel) -> TournamentRule:
        return TournamentRule(
            id=rule_orm.id,
            min_members=rule_orm.min_members,
            max_members=rule_orm.max_members,
            min_teams=rule_orm.min_teams,
            max_teams=rule_orm.max_teams,
            created_at=rule_orm.created_at,
            updated_at=rule_orm.updated_at,
            validation_list=rule_orm.validation_list or [],
            access_type=TournamentAccessType(rule_orm.access_type),
        )

    @staticmethod
    def _tournament_to_domain(tournament_orm: TournamentModel) -> Tournament:
        rule = TournamentRepositoryPostgresql._rule_to_domain(
            tournament_orm.tournament_rule
        )
        return Tournament(
            id=tournament_orm.id,
            name=tournament_orm.name,
            description=tournament_orm.description,
            date_start=tournament_orm.date_start,
            date_end=tournament_orm.date_end,
            tournament_rule=rule,
            state=TournamentState(tournament_orm.state),
            creator_user_id=tournament_orm.creator_user_id,
            category=TournamentCategory(tournament_orm.category),
            teams=[],
        )

    @staticmethod
    def _rule_to_orm(rule: TournamentRule) -> TournamentRuleModel:
        return TournamentRuleModel(
            id=rule.id,
            min_members=rule.min_members,
            max_members=rule.max_members,
            min_teams=rule.min_teams,
            max_teams=rule.max_teams,
            access_type=rule.access_type.value,
            validation_list=rule.validation_list,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )

    @staticmethod
    def _tournament_to_orm(tournament: Tournament) -> TournamentModel:
        rule_orm = TournamentRepositoryPostgresql._rule_to_orm(
            tournament.tournament_rule
        )
        return TournamentModel(
            id=tournament.id,
            name=tournament.name,
            description=tournament.description,
            date_start=tournament.date_start,
            date_end=tournament.date_end,
            state=tournament.state.value,
            category=tournament.category.value,
            creator_user_id=tournament.creator_user_id,
            tournament_rule=rule_orm,
        )

    # -------------------------------------------------------------------------
    # IMPLEMENTACIÓN DEL PUERTO
    # -------------------------------------------------------------------------

    def save(self, tournament: Tournament) -> None:
        rule = tournament.tournament_rule
        rule_orm = TournamentRuleModel(
            id=rule.id,
            min_members=rule.min_members,
            max_members=rule.max_members,
            min_teams=rule.min_teams,
            max_teams=rule.max_teams,
            access_type=rule.access_type.value,
            validation_list=rule.validation_list,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )
        rule_orm.save()

        TournamentModel.objects.create(
            id=tournament.id,
            name=tournament.name,
            description=tournament.description,
            date_start=tournament.date_start,
            date_end=tournament.date_end,
            state=tournament.state.value,
            category=tournament.category.value,
            creator_user_id=tournament.creator_user_id,
            tournament_rule=rule_orm,
        )

    def find_by_id(self, id: str) -> Tournament | None:
        try:
            tournament_orm = TournamentModel.objects.select_related(
                "tournament_rule"
            ).get(pk=id)
            return self._tournament_to_domain(tournament_orm)
        except TournamentModel.DoesNotExist:
            return None

    def find_all(self) -> list[Tournament]:
        tournaments_orm = TournamentModel.objects.select_related(
            "tournament_rule"
        ).all()
        return [self._tournament_to_domain(t) for t in tournaments_orm]

    def find_by_team_id(self, team_id: str) -> list[Tournament]:
        # Se consultará a través del modelo TournamentTeam cuando esté disponible
        raise NotImplementedError("Requiere el modelo TournamentTeamModel")

    def delete(self, id: str) -> None:
        TournamentModel.objects.filter(pk=id).delete()

    def update(self, tournament: Tournament) -> None:
        rule = tournament.tournament_rule
        TournamentRuleModel.objects.filter(pk=rule.id).update(
            min_members=rule.min_members,
            max_members=rule.max_members,
            min_teams=rule.min_teams,
            max_teams=rule.max_teams,
            access_type=rule.access_type.value,
            validation_list=rule.validation_list,
            updated_at=rule.updated_at,
        )
        TournamentModel.objects.filter(pk=tournament.id).update(
            name=tournament.name,
            description=tournament.description,
            date_start=tournament.date_start,
            date_end=tournament.date_end,
            state=tournament.state.value,
            category=tournament.category.value,
            creator_user_id=tournament.creator_user_id,
        )

    def find_by_name(self, name: str) -> list[Tournament] | None:
        tournaments_orm = TournamentModel.objects.select_related(
            "tournament_rule"
        ).filter(name__icontains=name)
        if not tournaments_orm.exists():
            return None
        return [self._tournament_to_domain(t) for t in tournaments_orm]

    def recover_tournament_rules(self, tournament_id: str) -> TournamentRule | None:
        try:
            tournament_orm = TournamentModel.objects.select_related(
                "tournament_rule"
            ).get(pk=tournament_id)
            return self._rule_to_domain(tournament_orm.tournament_rule)
        except TournamentModel.DoesNotExist:
            return None