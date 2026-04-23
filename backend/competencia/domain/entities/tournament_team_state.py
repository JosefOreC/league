import enum

class TournamentTeamState(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DISQUALIFIED = "disqualified"
    RETIRATED = "retirated"