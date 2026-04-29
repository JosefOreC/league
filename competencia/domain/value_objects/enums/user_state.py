import enum

class UserState(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    BANNED = "banned"
    PENDING = "pending"
    NOT_VERIFIED = "not_verified"

    def from_value(value: str) -> 'UserState':
        for state in UserState:
            if state.value == value:
                return state
        raise ValueError(f"Estado inválido: {value}")