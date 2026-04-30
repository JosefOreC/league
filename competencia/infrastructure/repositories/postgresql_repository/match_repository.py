from ....domain.ports.match_repository import MatchRepository
from ....domain.entities.match import Match
from ...adapters.output.models import MatchModel, TournamentModel, TeamModel, GroupModel
from uuid import uuid4

class MatchRepositoryPostgresql(MatchRepository):
    
    @staticmethod
    def _match_to_domain(match_orm: MatchModel) -> Match:
        return Match(
            id=match_orm.id,
            tournament_id=match_orm.tournament_id,
            ronda=match_orm.ronda,
            posicion_en_ronda=match_orm.posicion_en_ronda,
            equipo_local_id=match_orm.equipo_local_id,
            equipo_visitante_id=match_orm.equipo_visitante_id,
            es_bye=match_orm.es_bye,
            es_descanso=match_orm.es_descanso,
            grupo_id=match_orm.grupo_id,
            fase=match_orm.fase,
            estado=match_orm.estado,
            ganador_id=match_orm.ganador_id,
            partido_siguiente_id=match_orm.partido_siguiente_id,
            fecha_programada=match_orm.fecha_programada
        )

    def save(self, match: Match):
        tournament = TournamentModel.objects.get(pk=match.tournament_id)
        local = TeamModel.objects.get(pk=match.equipo_local_id) if match.equipo_local_id else None
        visitor = TeamModel.objects.get(pk=match.equipo_visitante_id) if match.equipo_visitante_id else None
        group = GroupModel.objects.get(pk=match.grupo_id) if match.grupo_id else None
        
        # Siguiente partido (si existe)
        next_match = MatchModel.objects.get(pk=match.partido_siguiente_id) if match.partido_siguiente_id else None

        MatchModel.objects.update_or_create(
            id=match.id,
            defaults={
                "tournament": tournament,
                "ronda": match.ronda,
                "posicion_en_ronda": match.posicion_en_ronda,
                "equipo_local": local,
                "equipo_visitante": visitor,
                "es_bye": match.es_bye,
                "es_descanso": match.es_descanso,
                "grupo": group,
                "fase": match.fase,
                "estado": match.estado,
                "ganador_id": match.ganador_id,
                "partido_siguiente": next_match,
                "fecha_programada": match.fecha_programada
            }
        )

    def find_by_id(self, id: str) -> Match | None:
        try:
            match_orm = MatchModel.objects.get(pk=id)
            return self._match_to_domain(match_orm)
        except MatchModel.DoesNotExist:
            return None

    def find_by_tournament(self, tournament_id: str) -> list[Match]:
        matches_orm = MatchModel.objects.filter(tournament_id=tournament_id)
        return [self._match_to_domain(m) for m in matches_orm]

    def find_by_group(self, group_id: str) -> list[Match]:
        matches_orm = MatchModel.objects.filter(grupo_id=group_id)
        return [self._match_to_domain(m) for m in matches_orm]

    def delete_by_tournament(self, tournament_id: str):
        MatchModel.objects.filter(tournament_id=tournament_id).delete()
