from ...domain.ports.match_repository import MatchRepository
from ...domain.ports.standing_repository import StandingRepository
from ...domain.entities.standing import Standing

class CalculateStandingsUseCase:
    def __init__(self, match_repository: MatchRepository, standing_repository: StandingRepository):
        self.__match_repository = match_repository
        self.__standing_repository = standing_repository

    def execute(self, tournament_id: str):
        matches = self.__match_repository.find_by_tournament(tournament_id)
        finished_matches = [m for m in matches if m.estado == "FINISHED"]

        standings = {} # team_id -> Standing object

        for m in finished_matches:
            if m.es_bye or m.es_descanso: continue
            
            # Local
            if m.equipo_local_id not in standings:
                standings[m.equipo_local_id] = Standing(tournament_id, m.equipo_local_id, m.grupo_id)
            
            # Visitante
            if m.equipo_visitante_id not in standings:
                standings[m.equipo_visitante_id] = Standing(tournament_id, m.equipo_visitante_id, m.grupo_id)

            l_std = standings[m.equipo_local_id]
            v_std = standings[m.equipo_visitante_id]

            if m.ganador_id == m.equipo_local_id:
                l_std.update(win=True, pts=3)
                v_std.update(loss=True, pts=0)
            elif m.ganador_id == m.equipo_visitante_id:
                v_std.update(win=True, pts=3)
                l_std.update(loss=True, pts=0)
            else:
                l_std.update(draw=True, pts=1)
                v_std.update(draw=True, pts=1)

        # Guardar y ordenar por puntos
        sorted_standings = sorted(standings.values(), key=lambda x: (x.puntos, x.diferencia_puntaje), reverse=True)
        
        self.__standing_repository.delete_by_tournament(tournament_id)
        for i, s in enumerate(sorted_standings):
            # Hack para setear posición (propiedad privada en el dominio para esta demo)
            s._Standing__posicion = i + 1
            self.__standing_repository.save(s)

        return [s.to_dict() for s in sorted_standings]
