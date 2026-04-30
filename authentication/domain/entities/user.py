from ..value_objects.enum.system_rol import SystemRol
from ..value_objects.enum.user_state import UserState
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import uuid

class User:

    __MAX_ATTEMPTS = 5
    __MAX_AGE = 80
    __MIN_AGE = 3
    __MIN_PASSWORD_LENGTH = 8
    __MIN_LOCK_TIME = 15

    def __init__(self, id: uuid.UUID, email: str, password_hash: str | None, name: str, 
                rol: SystemRol, state: UserState, birth_date: datetime | None, attempts: int | None, 
                blocked_until: datetime | None, created_at: datetime | None, updated_at: datetime | None, 
                last_login: datetime | None):
        self.__id = id
        self.__email = email
        self.__password_hash = password_hash
        self.__name = name
        self.__rol = rol
        self.__state = state
        self.__birth_date = birth_date
        self.__attempts = attempts
        self.__blocked_until = blocked_until
        self.__created_at = created_at
        self.__updated_at = updated_at
        self.__last_login = last_login
        
    @classmethod
    def create_user(cls, email: str, rol: SystemRol, name: str, birth_date: datetime, password_hash) -> "User":
        id = uuid.uuid4()
        state = UserState.NOT_VERIFIED
        attempts = 0
        blocked_until = None
        created_at = datetime.now(ZoneInfo("America/Lima"))
        updated_at = datetime.now(ZoneInfo("America/Lima"))

        last_login = None
        return cls(id=id, email=email, password_hash=password_hash, 
                    name=name, rol=rol, state=state, 
                    birth_date=birth_date, attempts=attempts, 
                    blocked_until=blocked_until, created_at=created_at, 
                    updated_at=updated_at, 
                    last_login=last_login)

    @property
    def id(self) -> uuid.UUID:
        return self.__id
    
    @property
    def last_login(self) -> datetime | None:
        return self.__last_login

    @property
    def email(self) -> str:
        return self.__email
    
    @property
    def password_hash(self) -> str:
        return self.__password_hash
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def rol(self) -> SystemRol:
        return self.__rol
    
    @property
    def state(self) -> UserState:
        return self.__state
    
    @property
    def birth_date(self) -> datetime:
        return self.__birth_date
    
    @property
    def attempts(self) -> int:
        return self.__attempts
    
    @property
    def blocked_until(self) -> datetime | None:
        return self.__blocked_until
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    @property
    def updated_at(self) -> datetime:
        return self.__updated_at

    def __calculate_age(self) -> int:
        hoy = datetime.now(ZoneInfo("America/Lima"))
        edad = hoy.year - self.__birth_date.year
        if hoy.month < self.__birth_date.month or (hoy.month == self.__birth_date.month and hoy.day < self.__birth_date.day):
            edad -= 1
        return edad
    

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError("El nombre debe ser una cadena no vacía")
        self.__name = name
        self.__touch()
    
    @email.setter
    def email(self, email: str):
        if not isinstance(email, str) or not email:
            raise ValueError("El email debe ser una cadena no vacía")
        if '@' not in email:
            raise ValueError("El email debe contener un @")
        if '.' not in email:
            raise ValueError("El email debe contener un .")
        self.__email = email
    
    @birth_date.setter
    def birth_date(self, birth_date: datetime):
        if not isinstance(birth_date, datetime):
            raise ValueError("La fecha de nacimiento debe ser una fecha")
        
        # Guardamos el anterior por si falla la validación
        old_birth_date = self.__birth_date
        self.__birth_date = birth_date
        
        try:
            age = self.__calculate_age()
            if age > self.__MAX_AGE:
                raise ValueError(f"La edad no puede ser mayor a {self.__MAX_AGE} años")
            if age < self.__MIN_AGE:
                raise ValueError(f"La edad no puede ser menor a {self.__MIN_AGE} años")
            self.__age = age
        except ValueError:
            self.__birth_date = old_birth_date
            raise
            
        self.__touch()

    @password_hash.setter
    def password_hash(self, password_hash: str):
        self.__password_hash = password_hash
        self.__touch()
   
    def verify_password_security(self, password: str)->bool:
        if not isinstance(password, str) or not password:
            raise ValueError("La contraseña debe ser una cadena no vacía")
        if len(password) < self.__MIN_PASSWORD_LENGTH:
            raise ValueError(f"La contraseña debe tener al menos {self.__MIN_PASSWORD_LENGTH} caracteres")
        if not any(c.isdigit() for c in password):
            raise ValueError("La contraseña debe tener al menos un número")
        if not any(c.isupper() for c in password):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.islower() for c in password):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        return True

    @state.setter
    def state(self, state: UserState):
        if not isinstance(state, UserState):
            raise ValueError("El estado debe ser un estado")
        self.__state = state
    
    @rol.setter
    def rol(self, rol: SystemRol):
        if not isinstance(rol, SystemRol):
            raise ValueError("El rol debe ser un rol")
        self.__touch()
        self.__rol = rol
    
    def is_locked(self) -> bool:
        if self.__blocked_until is None:
            return False
        if self.__blocked_until < datetime.now(ZoneInfo("America/Lima")):
            self.unlock()
            return False
        return True
        
    def lock(self, minutes: int) -> None:
        self.__blocked_until = datetime.now(ZoneInfo("America/Lima")) + timedelta(minutes=minutes)
        self.__attempts = 0
        self.__state = UserState.BLOCKED
    
    def increment_attempts(self) -> None:
        self.__attempts += 1
        if self.__attempts >= self.__MAX_ATTEMPTS:
            self.lock(self.__MIN_LOCK_TIME)
        
    def reset_attempts(self) -> None:
        self.__attempts = 0
        self.__blocked_until = None
        self.__state = UserState.ACTIVE
    
    def update_last_login(self, last_login: datetime) -> None:
        self.__last_login = last_login
    
    def time_to_unlock(self) -> int:
        if self.__blocked_until is None:
            return 0
        if self.__blocked_until < datetime.now(ZoneInfo("America/Lima")):
            return 0
        return int((self.__blocked_until - datetime.now(ZoneInfo("America/Lima"))).total_seconds() / 60)
    
    def unlock(self) -> None:
        self.__blocked_until = None
        self.__attempts = 0
        self.__state = UserState.ACTIVE

    def __touch(self) -> None:
        self.__updated_at = datetime.now(ZoneInfo("America/Lima"))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.__id == other.__id
    
    def to_internal_dict(self) -> dict:
        return {
            "id": str(self.__id),
            "email": self.__email,
            "name": self.__name,
            "rol": self.__rol.value,
            "state": self.__state.value,
            "birth_date": self.__birth_date.strftime("%Y-%m-%d"),
            "attempts": self.__attempts,
            "blocked_until": self.__blocked_until,
            "created_at": self.__created_at,
            "updated_at": self.__updated_at,
            "last_login": self.__last_login
        }
    
    def to_external_dict(self) -> dict:
        return {
            "id": str(self.__id),
            "email": self.__email,
            "name": self.__name,
            "rol": self.__rol.value,
            "state": self.__state.value,
            "birth_date": self.__birth_date.strftime("%Y-%m-%d")
        }