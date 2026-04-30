from ....domain.ports.tournament_repository import TournamentRepository
from ....domain.entities.tournament import Tournament
from ....domain.entities.tournament_rule import TournamentRule
from ....domain.entities.criteria import Criteria
from ....domain.entities.tournament_member import TournamentMember
from ....domain.value_objects.enums.tournament_state import TournamentState
from ....domain.value_objects.enums.tournament_access_type import TournamentAccessType
from ....domain.value_objects.enums.tournament_category import TournamentCategory
from ....domain.entities.team import Team
from ....domain.entities.tournament_team import TournamentTeam
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
    def _team_to_domain(team_orm) -> Team:
        from .team_repository import TeamRepositoryPostgresql
        return TeamRepositoryPostgresql._team_to_domain(team_orm)

    @staticmethod
    def _tournament_team_to_domain(team_orm) -> TournamentTeam:
        from ....domain.value_objects.enums.tournament_team_state import TournamentTeamState
        
        state_map = {
            "PENDIENTE": TournamentTeamState.PENDING,
            "APROBADO": TournamentTeamState.ACCEPTED,
            "RECHAZADO": TournamentTeamState.REFUSED,
            "DISQUALIFIED": TournamentTeamState.DISQUALIFIED,
            "RETIRATED": TournamentTeamState.RETIRATED
        }
        
        team_domain = TournamentRepositoryPostgresql._team_to_domain(team_orm)
        return TournamentTeam(
            id=team_orm.id,
            tournament_id=team_orm.tournament_id,
            state=state_map.get(team_orm.estado_inscripcion, TournamentTeamState.PENDING),
            member_in_tournament_func=None, # Will be set by Tournament entity if needed
            team=team_domain,
            qualify_score_team=[]
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
            teams=[
                TournamentRepositoryPostgresql._tournament_team_to_domain(t)
                for t in tournament_orm.teams.all()
            ],
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
        rule_orm, _ = TournamentRuleModel.objects.update_or_create(
            id=rule.id,
            defaults={
                "min_members": rule.min_members,
                "max_members": rule.max_members,
                "min_teams": rule.min_teams,
                "max_teams": rule.max_teams,
                "access_type": rule.access_type.value,
                "validation_list": list(rule.validation_list),
                "created_at": rule.created_at,
                "updated_at": rule.updated_at,
                "date_start_inscription": rule.date_start_inscription,
                "date_end_inscription": rule.date_end_inscription,
            }
        )

        # 2. Guardar el torneo
        tournament_orm, _ = TournamentModel.objects.update_or_create(
            id=tournament.id,
            defaults={
                "name": tournament.name,
                "description": tournament.description,
                "date_start": tournament.date_start,
                "date_end": tournament.date_end,
                "state": tournament.state.value,
                "category": tournament.category.value,
                "creator_user_id": tournament.creator_user_id,
                "tournament_rule": rule_orm,
                "config_tournament": tournament.config_tournament.to_dict() if tournament.config_tournament else {},
            }
        )

        # 3. Guardar members del torneo
        member_orms = []
        for member in tournament.users_tournaments:
            m_orm, _ = TournamentMemberModel.objects.update_or_create(
                user_id=member.user_id,
                tournament_id=tournament.id,
                defaults={
                    "id": str(uuid4()) if not hasattr(member, 'id') else member.id,
                    "rol": member.rol.value,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            member_orms.append(m_orm)
        tournament_orm.tournament_members.set(member_orms)

        # 4. Guardar criterias
        if tournament.tournament_evaluation:
            for criteria in tournament.tournament_evaluation.criterias:
                CriteriaModel.objects.update_or_create(
                    id=criteria.id,
                    defaults={
                        "name": criteria.name,
                        "description": criteria.description,
                        "value": criteria.value,
                        "min_value_qualification": criteria.min_value_qualification,
                        "max_value_qualification": criteria.max_value_qualification,
                        "created_at": criteria.created_at,
                        "updated_at": criteria.updated_at,
                        "tournament": tournament_orm
                    }
                )

        # 5. Sincronizar equipos (TournamentTeams)
        # Nota: TeamModel en DB es el equivalente a TournamentTeam + Team en dominio
        from .team_repository import TeamRepositoryPostgresql
        team_repo = TeamRepositoryPostgresql()
        for tt in tournament.get_teams():
            # El estado del TournamentTeam se guarda en TeamModel.estado_inscripcion
            # Mapeamos de vuelta si es necesario antes de guardar
            tt.team.estado_inscripcion = tt.state.value.upper() 
            if tt.team.estado_inscripcion == "ACCEPTED": tt.team.estado_inscripcion = "APROBADO"
            if tt.team.estado_inscripcion == "PENDING": tt.team.estado_inscripcion = "PENDIENTE"
            if tt.team.estado_inscripcion == "REFUSED": tt.team.estado_inscripcion = "RECHAZADO"
            
            team_repo.save(tt.team)

    def update(self, tournament: Tournament) -> None:
        self.save(tournament) # El método save ya usa update_or_create

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