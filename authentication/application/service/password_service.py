import bcrypt
from ...domain.entities.user import User
import bcrypt

class PasswordService:
    def __init__(self):
        pass
    def verify_password(self, user:User, password) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))

    def change_password(self, user, new_password) -> bool:
        user.verify_password_security(new_password)
        new_password_hash = self.encrypt_password(new_password)
        user.password_hash = new_password_hash
        return True
        
    def encrypt_password(self, password: str) -> str:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return password_hash.decode('utf-8')
    