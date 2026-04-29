

class ConfigTournament:
    
    def validate(self, tournament_teams_count: int) -> bool:
        raise NotImplementedError("Subclases deben implementar este método")

    def to_dict(self):
        return {
            
        }
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    def __eq__(self, other):
        if not isinstance(other, ConfigTournament):
            return False
        return self.to_dict() == other.to_dict()
    