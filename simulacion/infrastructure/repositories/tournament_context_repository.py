"""
Repositorio concreto que implementa TournamentContextPort.

Usa UNA SOLA consulta SQL mediante select_related + prefetch_related
para recuperar el torneo, sus criterios y el equipo del representante
(cumpliendo RNF2-001 y la regla de no-N+1).

No se crean modelos ORM propios porque los de competencia/ cubren
completamente los datos requeridos por HU-SIM-01 (TournamentModel,
CriteriaModel, TeamModel, ParticipantModel).
"""
from typing import Optional

from django.db.models import Count, Prefetch

from competencia.infrastructure.adapters.output.models import (
    CriteriaModel,
    TeamModel,
    TournamentModel,
)
from simulacion.domain.entities.simulation_context import (
    CriterioInfo,
    SimulationContext,
    TeamInfo,
    TournamentInfo,
)
from simulacion.domain.ports.tournament_context_port import TournamentContextPort
from simulacion.application.use_cases.get_simulation_context_use_case import (
    TeamNotApprovedError,
)


class TournamentContextRepository(TournamentContextPort):
    """
    Adaptador de salida (driven adapter) que obtiene el contexto de simulación
    en una sola consulta SQL optimizada con prefetch_related.

    Patrón de consulta:
        1 query → TournamentModel filtrado por pk.
        + 1 prefetch → CriteriaModel ordenado por name.
        + 1 prefetch → TeamModel filtrado por representante_id='APROBADO'
                        con Count('participants') anotado.
    Total: ≤ 3 queries (conforme a assertNumQueries en los tests).
    """

    def get_context(
        self,
        tournament_id: str,
        representante_id: str,
    ) -> Optional[SimulationContext]:
        """
        Recupera el contexto en una sola consulta SQL principal con prefetches.

        Returns:
            SimulationContext si el torneo existe y el representante tiene equipo aprobado.
            None si el torneo no existe.

        Raises:
            TeamNotApprovedError: si el torneo existe pero no hay equipo aprobado
                                  para este representante.
        """
        tournament_qs = (
            TournamentModel.objects
            .prefetch_related(
                Prefetch(
                    'criterias',
                    queryset=CriteriaModel.objects.order_by('name'),
                ),
                Prefetch(
                    'teams',
                    queryset=(
                        TeamModel.objects
                        .filter(
                            representante_id=representante_id,
                            estado_inscripcion='APROBADO',
                        )
                        .annotate(participants_count=Count('participants'))
                    ),
                ),
            )
            .filter(pk=tournament_id)
        )

        tournament = tournament_qs.first()

        # Torneo no encontrado → devuelve None (el use case lo convierte en 404)
        if tournament is None:
            return None

        # Intentamos obtener el equipo aprobado del representante
        team = next(iter(tournament.teams.all()), None)

        # Torneo existe pero el representante no tiene equipo aprobado → 403
        if team is None:
            raise TeamNotApprovedError(
                "No tiene un equipo aprobado en este torneo"
            )

        # Construimos el SimulationContext con objetos de valor puros
        tournament_info = TournamentInfo(
            id=str(tournament.id),
            name=tournament.name,
            state=tournament.state,
            category=tournament.category,
        )

        team_info = TeamInfo(
            id=str(team.id),
            name=team.name,
            nivel_tecnico_declarado=team.nivel_tecnico_declarado,
            participants_count=team.participants_count,
        )

        criterios = [
            CriterioInfo(
                id=str(c.id),
                name=c.name,
                description=c.description,
                peso=float(c.value),
                min_qualification=float(c.min_value_qualification),
                max_qualification=float(c.max_value_qualification),
            )
            for c in tournament.criterias.all()
        ]

        return SimulationContext(
            tournament=tournament_info,
            team=team_info,
            criterios=criterios,
        )
