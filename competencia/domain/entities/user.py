
from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState

class User: 
    def __init__(self,id:int, name:str, email:str, rol:SystemRol, state:UserState):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__rol = rol
        self.__state = state
    
    @property
    def id(self) -> int:
        return self.__id
    
    @id.setter
    def id(self, id: int):
        if not isinstance(id, int) or not id:
            raise ValueError("El id debe ser un entero no vacío")
        self.__id = id
    
    @property
    def rol(self) -> SystemRol:
        return self.__rol
    
    @rol.setter
    def rol(self, rol: SystemRol):
        if not isinstance(rol, SystemRol):
            raise ValueError("El rol debe ser un rol")
        self.__rol = rol
    
    @property
    def state(self) -> UserState:
        return self.__state
    
    @state.setter
    def state(self, state: UserState):
        if not isinstance(state, UserState):
            raise ValueError("El estado debe ser un estado")
        self.__state = state

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def rol(self) -> SystemRol:
        return self.__rol

    @property
    def email(self) -> str:
        return self.__email

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError("El nombre debe ser una cadena no vacía")
        self.__name = name
    
    @email.setter
    def email(self, email: str):
        if not isinstance(email, str) or not email:
            raise ValueError("El email debe ser una cadena no vacía")
        self.__email = email
    

    @state.setter
    def state(self, state: UserState):
        if not isinstance(state, UserState):
            raise ValueError("El estado debe ser un estado")
        self.__state = state
    
    @rol.setter
    def rol(self, rol: SystemRol):
        if not isinstance(rol, SystemRol):
            raise ValueError("El rol debe ser un rol")
        self.__rol = rol
