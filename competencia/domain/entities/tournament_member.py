from ..value_objects.enums.tournament_rol import TournamentRol


class TournamentMember:
    def __init__(self, user_id: str, tournament_id: str, rol: TournamentRol):
        if not user_id:
            raise ValueError("El usuario debe tener un id")
        if not rol:
            raise ValueError("El usuario debe tener al menos un rol")
        self.__user_id = user_id
        self.__tournament_id = tournament_id   # ← bug fix: ahora se asigna
        self.__rol = rol

    @property
    def user_id(self) -> str:
        return self.__user_id

    @property
    def tournament_id(self) -> str:
        return self.__tournament_id

    @property
    def rol(self) -> TournamentRol:
        return self.__rol

    @rol.setter
    def rol(self, rol: TournamentRol):
        if not isinstance(rol, TournamentRol):
            raise ValueError("El rol debe ser un TournamentRol")
        self.__rol = rol

    def to_dict(self) -> dict:
        return {
            "user_id": self.__user_id,
            "tournament_id": self.__tournament_id,
            "rol": self.__rol.value,
        }

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TournamentMember):
            return False
        return self.user_id == o.user_id

    def __hash__(self) -> int:
        return hash(self.user_id)