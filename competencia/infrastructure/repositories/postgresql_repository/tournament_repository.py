from ....domain.ports.tournament_repository import TournamentRepository
from ....domain.entities.tournament import Tournament
from ....domain.entities.tournament_rule import TournamentRule
from ....domain.entities.criteria import Criteria
from ....domain.entities.tournament_member import TournamentMember
from ....domain.value_objects.enums.tournament_state import TournamentState
from ....domain.value_objects.enums.tournament_access_type import TournamentAccessType
from ....domain.value_objects.enums.tournament_category import TournamentCategory
from ....domain.value_objects.enums.tournament_rol import TournamentRol
from ...adapters.output.models import (
    TournamentModel,
    TournamentRuleModel,
    CriteriaModel,
    TournamentMemberModel,
)
from ....domain.value_objects.config_tournament.config_tournament_factory import ConfigTournamentFactory
from ....domain.value_objects.config_tournament.tournament_evaluation import TournamentEvaluation
from datetime import datetime
from uuid import uuid4


class TournamentRepositoryPostgresql(TournamentRepository):

    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # MAPPERS: ORM → DOMINIO
    # -------------------------------------------------------------------------

    @staticmethod
    def _criteria_to_domain(criteria_orm: CriteriaModel) -> Criteria:
        return Criteria(
            id=criteria_orm.id,
            name=criteria_orm.name,
            description=criteria_orm.description,
            min_value_qualification=criteria_orm.min_value_qualification,
            max_value_qualification=criteria_orm.max_value_qualification,
            created_at=criteria_orm.created_at,
            updated_at=criteria_orm.updated_at,
            value=criteria_orm.value,
        )

    @staticmethod
    def _member_to_domain(member_orm: TournamentMemberModel) -> TournamentMember:
        return TournamentMember(
            user_id=member_orm.user_id,
            tournament_id=member_orm.tournament_id,
            rol=TournamentRol(member_orm.rol),
        )

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
            date_start_inscription=rule_orm.date_start_inscription,
            date_end_inscription=rule_orm.date_end_inscription,
        )

    @staticmethod
    def _tournament_to_domain(tournament_orm: TournamentModel) -> Tournament:
        rule = TournamentRepositoryPostgresql._rule_to_domain(
            tournament_orm.tournament_rule
        )
        members = [
            TournamentRepositoryPostgresql._member_to_domain(m)
            for m in tournament_orm.tournament_members.all()
        ]
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
            users_tournaments=members,
            teams=[],
            config_tournament=ConfigTournamentFactory.create_config_tournament(
                tournament_orm.config_tournament.get("type", "knockout"),
                tournament_orm.config_tournament.get("config", {})
            ) if tournament_orm.config_tournament else None,
            tournament_evaluation=TournamentEvaluation(
                criteria_list=[
                    TournamentRepositoryPostgresql._criteria_to_domain(c)
                    for c in tournament_orm.criterias.all()
                ]
            ),
        )

    # -------------------------------------------------------------------------
    # IMPLEMENTACIÓN DEL PUERTO
    # -------------------------------------------------------------------------

    def save(self, tournament: Tournament) -> None:
        now = datetime.now()
        rule = tournament.tournament_rule

        # 1. Guardar regla del torneo
        rule_orm = TournamentRuleModel(
            id=rule.id,
            min_members=rule.min_members,
            max_members=rule.max_members,
            min_teams=rule.min_teams,
            max_teams=rule.max_teams,
            access_type=rule.access_type.value,
            validation_list=list(rule.validation_list),
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            date_start_inscription=rule.date_start_inscription,
            date_end_inscription=rule.date_end_inscription,
        )
        rule_orm.save()

        # 2. Guardar members del torneo
        member_orms = []
        for member in tournament.users_tournaments:
            member_orm = TournamentMemberModel.objects.create(
                id=str(uuid4()),
                user_id=member.user_id,
                tournament_id=tournament.id,
                rol=member.rol.value,
                created_at=now,
                updated_at=now,
            )
            member_orms.append(member_orm)

        # 3. Crear el torneo y vincular members (M2M)
        tournament_orm = TournamentModel.objects.create(
            id=tournament.id,
            name=tournament.name,
            description=tournament.description,
            date_start=tournament.date_start,
            date_end=tournament.date_end,
            state=tournament.state.value,
            category=tournament.category.value,
            creator_user_id=tournament.creator_user_id,
            tournament_rule=rule_orm,
            config_tournament=tournament.config_tournament.to_dict() if tournament.config_tournament else {},
        )
        tournament_orm.tournament_members.set(member_orms)

        # 4. Guardar criterias en la tabla
        if tournament.tournament_evaluation:
            for criteria in tournament.tournament_evaluation.criterias:
                CriteriaModel.objects.create(
                    id=criteria.id,
                    name=criteria.name,
                    description=criteria.description,
                    value=criteria.value,
                    min_value_qualification=criteria.min_value_qualification,
                    max_value_qualification=criteria.max_value_qualification,
                    created_at=criteria.created_at,
                    updated_at=criteria.updated_at,
                    tournament=tournament_orm
                )

    def find_by_id(self, id: str) -> Tournament | None:
        try:
            tournament_orm = (
                TournamentModel.objects
                .select_related("tournament_rule")
                .prefetch_related("tournament_members", "criterias")
                .get(pk=id)
            )
            return self._tournament_to_domain(tournament_orm)
        except TournamentModel.DoesNotExist:
            return None

    def find_all(self) -> list[Tournament]:
        tournaments_orm = (
            TournamentModel.objects
            .select_related("tournament_rule")
            .prefetch_related("tournament_members", "criterias")
            .all()
        )
        return [self._tournament_to_domain(t) for t in tournaments_orm]

    def find_by_team_id(self, team_id: str) -> list[Tournament]:
        raise NotImplementedError("Requiere el modelo TournamentTeamModel")

    def delete(self, id: str) -> None:
        TournamentModel.objects.filter(pk=id).delete()

    def update(self, tournament: Tournament) -> None:
        now = datetime.now()
        rule = tournament.tournament_rule

        # 1. Actualizar regla
        TournamentRuleModel.objects.filter(pk=rule.id).update(
            min_members=rule.min_members,
            max_members=rule.max_members,
            min_teams=rule.min_teams,
            max_teams=rule.max_teams,
            access_type=rule.access_type.value,
            validation_list=list(rule.validation_list),
            updated_at=rule.updated_at,
            date_start_inscription=rule.date_start_inscription,
            date_end_inscription=rule.date_end_inscription,
        )

        # 3. Actualizar torneo
        TournamentModel.objects.filter(pk=tournament.id).update(
            name=tournament.name,
            description=tournament.description,
            date_start=tournament.date_start,
            date_end=tournament.date_end,
            state=tournament.state.value,
            category=tournament.category.value,
            creator_user_id=tournament.creator_user_id,
            config_tournament=tournament.config_tournament.to_dict() if tournament.config_tournament else {},
        )

        # Sincronizar criterias: borrar antiguos y crear nuevos
        tournament_orm = TournamentModel.objects.get(pk=tournament.id)
        tournament_orm.criterias.all().delete()
        if tournament.tournament_evaluation:
            for criteria in tournament.tournament_evaluation.criterias:
                CriteriaModel.objects.create(
                    id=criteria.id,
                    name=criteria.name,
                    description=criteria.description,
                    value=criteria.value,
                    created_at=criteria.created_at,
                    updated_at=criteria.updated_at,
                    tournament=tournament_orm
                )

        # 4. Sincronizar members M2M: borrar los huérfanos y re-crear
        tournament_orm = TournamentModel.objects.get(pk=tournament.id)
        old_member_ids = list(
            tournament_orm.tournament_members.values_list("id", flat=True)
        )
        tournament_orm.tournament_members.clear()
        TournamentMemberModel.objects.filter(id__in=old_member_ids).delete()

        new_member_orms = []
        for member in tournament.users_tournaments:
            member_orm = TournamentMemberModel.objects.create(
                id=str(uuid4()),
                user_id=member.user_id,
                tournament_id=tournament.id,
                rol=member.rol.value,
                created_at=now,
                updated_at=now,
            )
            new_member_orms.append(member_orm)
        tournament_orm.tournament_members.set(new_member_orms)

    def find_by_name(self, name: str) -> list[Tournament] | None:
        tournaments_orm = (
            TournamentModel.objects
            .select_related("tournament_rule")
            .prefetch_related("tournament_members")
            .filter(name__icontains=name)
        )
        if not tournaments_orm.exists():
            return None
        return [self._tournament_to_domain(t) for t in tournaments_orm]

    def recover_tournament_rules(self, tournament_id: str) -> TournamentRule | None:
        try:
            tournament_orm = (
                TournamentModel.objects
                .select_related("tournament_rule")
                .get(pk=tournament_id)
            )
            return self._rule_to_domain(tournament_orm.tournament_rule)
        except TournamentModel.DoesNotExist:
            return None