import bcrypt
from datetime import datetime
import bcrypt
from .system_rol import SystemRol
from .user_state import UserState

class User: 
    def __init__(self,id:int, name:str, email:str, date_registered:datetime, birth_date:datetime, rol:SystemRol, state:UserState, password_hash:str=None):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__date_registered = date_registered
        self.__birth_date = birth_date
        self.__age = self.__calculate_age()
        self.__password_hash = password_hash
        self.__rol = SystemRol.from_value(rol)
        self.__state = UserState.from_value(state)
    
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

    def __calculate_age(self) -> int:
        hoy = datetime.now()
        edad = hoy.year - self.__birth_date.year
        if hoy.month < self.__birth_date.month or (hoy.month == self.__birth_date.month and hoy.day < self.__birth_date.day):
            edad -= 1
        return edad
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def rol(self) -> SystemRol:
        return self.__rol

    @property
    def email(self) -> str:
        return self.__email
    
    @property
    def date_registered(self) -> datetime:
        return self.__date_registered
    
    @property
    def age(self) -> int:
        return self.__age
    
    @property
    def birth_date(self) -> datetime:
        return self.__birth_date

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
    
    @date_registered.setter
    def date_registered(self, date_registered: datetime):
        if not isinstance(date_registered, datetime):
            raise ValueError("La fecha de registro debe ser una fecha")
        self.__date_registered = date_registered
    
    @birth_date.setter
    def birth_date(self, birth_date: datetime):
        if not isinstance(birth_date, datetime):
            raise ValueError("La fecha de nacimiento debe ser una fecha")
        age = self.__calculate_age()
        if age > 80:
            raise ValueError("La edad no puede ser mayor a 80 años")
        if age < 3:
            raise ValueError("La edad no puede ser menor a 3 años")
        self.__birth_date = birth_date
        self.__age = age

    @property
    def password(self) -> str:
        raise AttributeError("La contraseña no se puede obtener")
        
    @password.setter
    def password(self, password: str):
        if not isinstance(password, str) or not password:
            raise ValueError("La contraseña debe ser una cadena no vacía")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not any(c.isdigit() for c in password):
            raise ValueError("La contraseña debe tener al menos un número")
        if not any(c.isupper() for c in password):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.islower() for c in password):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        self.__password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.__password_hash)

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
    
    def can_participate(self) -> bool:
        return self.state == UserState.ACTIVE