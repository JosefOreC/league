from .user import User
from .system_rol import SystemRol
from .user_state import UserState
from .institution import Institution

class Team:
    def __init__(self, id:str, name:str, creator_user:User, teacher:User, institution:Institution, members:list[User], leader: User = None):
        self.__id = id
        if not isinstance(name, str) or not name or len(name) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        self.__name = name

        if not isinstance(institution, Institution):
            raise ValueError("La institución debe ser una institución")
        self.__institution = institution

        self.__members = []
        if not isinstance(creator_user, User) or creator_user.rol not in [SystemRol.MANAGER, SystemRol.ADMIN]:
            raise ValueError("El creador debe ser un usuario admin o manager")
        self.__creator_user = creator_user
        
        self.__validate_teacher(teacher)
        self.__teacher = teacher

        if len(members) < 1:
            raise ValueError("El equipo debe tener al menos 1 miembro")
        for member in members:
            self.add_member(member)
        
        self.__leader = None
        if leader is not None:
            self.__validate_leader(leader)
            self.__leader = leader
    
    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def creator_user(self) -> User:
        return self.__creator_user
    
    @property
    def members(self) -> tuple[User]:
        return tuple(self.__members)
    
    @property
    def leader(self) -> User:
        return self.__leader
    
    @property
    def institution(self) -> Institution:
        return self.__institution

    @property
    def teacher(self) -> User:
        return self.__teacher

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError("El nombre debe ser una cadena no vacía")
        if len(name) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        self.__name = name
    
        
    def add_member(self, member: User):
        if self.__validate_member(member):
            self.__members.append(member)
    
    def remove_member(self, member: User):
        if not self.contains_member(member):
            raise ValueError("El miembro no está en el equipo")
        new_members = []
        
        for m in self.__members:
            if m.id != member.id:
                new_members.append(m)
        
        if len(new_members) < 1:
            raise ValueError("El equipo debe tener al menos 1 miembro")
        
        self.__members = new_members
        if self.__leader and member.id == self.__leader.id:
            self.__leader = None

    def change_leader(self, leader: User):
        self.__validate_leader(leader)
        self.__leader = leader

    def change_teacher(self, teacher: User):
        self.__validate_teacher(teacher)
        self.__teacher = teacher
    
    def __validate_teacher(self, teacher:User) -> bool:
        if not isinstance(teacher, User):
            raise ValueError("El profesor debe ser un usuario")
        if teacher.rol != SystemRol.COACH:
            raise ValueError("El profesor debe ser un coach habilitado")
        if teacher.state != UserState.ACTIVE:
            raise ValueError("El profesor debe estar activo")
        return True

    def __validate_member(self, member:User) -> bool:
        if not isinstance(member, User):
            raise ValueError("El miembro debe ser un usuario")
        if member.state != UserState.ACTIVE:
            raise ValueError(f"El miembro {member.name} se encuentra inhabilitado para participar.")
        if member.rol != SystemRol.PARTICIPANT:
            raise ValueError("El miembro debe ser un participante")
        if member.id == self.__creator_user.id or member.id == self.__teacher.id:
            raise ValueError("El miembro no puede ser el creador o el profesor")
        if self.contains_member(member):
            raise ValueError(f"El miembro {member.name} ya está en el equipo")
        return True
    
    def __validate_leader(self, leader:User) -> bool:
        if not isinstance(leader, User):
            raise ValueError("El lider debe ser un usuario")
        if leader.rol != SystemRol.PARTICIPANT:
            raise ValueError("El lider debe ser un participante")
        if leader.state != UserState.ACTIVE:
            raise ValueError("El lider debe estar activo")
        if leader.id == self.__creator_user.id or leader.id == self.__teacher.id:
            raise ValueError("El lider no puede ser el creador o el profesor")
        if not self.contains_member(leader):
            raise ValueError(f"El lider {leader.name} no es miembro del equipo")
        return True
    
    def contains_member(self, member: User) -> bool:
        return any(member.id == m.id for m in self.__members)
    
    def has_leader(self) -> bool:
        return self.__leader is not None

    def validate_min_members(self) -> bool:
        return len(self.__members) >= 1

    def validate_max_members(self) -> bool:
        return len(self.__members) <= 16

