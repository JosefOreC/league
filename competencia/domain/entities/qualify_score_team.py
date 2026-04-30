class QualifyScoreTeam:
    def __init__(self, id_team:str, id_criteria:str, score:float):
        self.__id_team = id_team
        self.__id_criteria = id_criteria
        self.__score = score
    
    @property
    def id_team(self) -> str:
        return self.__id_team
    
    @property
    def id_criteria(self) -> str:
        return self.__id_criteria
    
    @property
    def score(self) -> float:
        return self.__score
    
    def to_dict(self) -> dict[str, any]:
        return {
            "id_team": self.id_team,
            "id_criteria": self.id_criteria,
            "score": self.score,
        }
    
  