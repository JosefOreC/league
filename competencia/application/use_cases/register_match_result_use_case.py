from ...domain.ports.match_repository import MatchRepository
from ...domain.ports.match_result_repository import MatchResultRepository
from ...domain.entities.match_result import MatchResult
from uuid import uuid4

class RegisterMatchResultUseCase:
    def __init__(self, match_repository: MatchRepository, match_result_repository: MatchResultRepository):
        self.__match_repository = match_repository
        self.__match_result_repository = match_result_repository

    def execute(self, match_id: str, results_data: list[dict]):
        match = self.__match_repository.find_by_id(match_id)
        if not match:
            raise ValueError("Partido no encontrado")

        results = []
        for rd in results_data:
            result = MatchResult(
                id=str(uuid4()),
                match_id=match_id,
                equipo_id=rd["equipo_id"],
                criterio_id=rd["criterio_id"],
                valor_registrado=rd["valor_registrado"],
                valor_normalizado=rd.get("valor_normalizado", rd["valor_registrado"]),
                estado_resultado="DEFINITIVE",
                registrado_por=rd["registrado_por"]
            )
            self.__match_result_repository.save(result)
            results.append(result)

        # Actualizar estado del partido si todos los resultados están
        match.set_winner(self._calculate_winner(results))
        self.__match_repository.save(match)
        
        return [r.to_dict() for r in results]

    def _calculate_winner(self, results):
        # Simplificación: Equipo con mayor valor normalizado total gana
        scores = {}
        for r in results:
            scores[r.equipo_id] = scores.get(r.equipo_id, 0) + r.valor_normalizado
        
        if not scores: return None
        return max(scores, key=scores.get)
