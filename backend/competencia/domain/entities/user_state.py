import enum

class UserState(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    BANNED = "banned"
    PENDING = "pending"
    NOT_VERIFIED = "not_verified"