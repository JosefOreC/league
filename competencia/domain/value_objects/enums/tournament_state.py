import enum

class TournamentState(enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    FINALIZED = "finalized"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
