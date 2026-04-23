import enum

class TournamentTeamState(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFUSED = "refused"
    DISQUALIFIED = "disqualified"
    RETIRATED = "retirated"