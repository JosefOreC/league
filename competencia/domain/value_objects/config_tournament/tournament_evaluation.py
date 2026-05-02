from ...entities.criteria import Criteria
from ...entities.qualify_score_team import QualifyScoreTeam

class TournamentEvaluation:
    def __init__(self, criteria_list: list[Criteria] = None):
        self.__criterias = criteria_list or []

    @classmethod
    def create(cls):
        return cls()

    @property
    def criterias(self) -> tuple[Criteria]:
        return tuple(self.__criterias)

    def _find_criteria(self, id_criteria:str) -> Criteria:
        for criteria in self.__criterias:
            if criteria.id == id_criteria:
                return criteria
        raise ValueError(f"Criterio con ID {id_criteria} no encontrado")

    def get_qualify_weighted_score_team(self, qualify_team_scores: list[QualifyScoreTeam]) -> float:
        weighted = sum(qts.score * self._find_criteria(qts.id_criteria).value for qts in qualify_team_scores)
        return weighted

    def add_criteria(self, criteria:Criteria):
        if criteria in self.__criterias:
            return
        self.__criterias.append(criteria)

    def remove_criteria(self, criteria:Criteria):
        if criteria not in self.__criterias:
            return
        self.__criterias.remove(criteria)
    
    def qualify_score(self, team, id_criteria:str, score:float) -> QualifyScoreTeam:
        criteria = self._find_criteria(id_criteria)
        if not criteria.min_value_qualification <= score <= criteria.max_value_qualification:
            raise ValueError("El puntaje debe estar entre el mínimo y el máximo")
        qualify_score_team = QualifyScoreTeam(team.id, id_criteria, score)
        return qualify_score_team


    def to_dict(self) -> dict[str, any]:
        return {
            "criterias": [criteria.to_dict() for criteria in self.criterias],
        }

    @classmethod
    def from_dict(cls, **data) -> "TournamentEvaluation":
        criterias = [Criteria.from_dict(**c) for c in data.get("criterias", [])]
        return cls(criteria_list=criterias)

    def valid_criterias(self)->bool:
        if sum(c.value for c in self.__criterias) != 1:
            raise ValueError("La suma de los valores debe ser 1")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TournamentEvaluation):
            return False
        return self.id == o.id

    def __hash__(self) -> int:
        return hash(self.id)
