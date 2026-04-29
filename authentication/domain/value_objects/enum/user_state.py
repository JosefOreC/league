import enum

class UserState(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    BLOCKED = "blocked"
    BANNED = "banned"
    PENDING = "pending"
    NOT_VERIFIED = "not_verified"

    @staticmethod
    def from_value(value: str) -> 'UserState':
        for state in UserState:
            if state.value == value:
                return state
        raise ValueError(f"Estado inválido: {value}")