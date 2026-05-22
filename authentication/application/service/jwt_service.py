import jwt
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ...domain.entities.user import User

class InvalidToken(Exception):
    pass

class JWTService:
    def __init__(self, SECRET_KEY):
        self.SECRET_KEY = SECRET_KEY

    def create_access_token(self, user: User) -> str:
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "rol": user.rol.value,
            "state": user.state.value,
            "exp": datetime.now(ZoneInfo("America/Lima")) + timedelta(minutes=15),
            "iat": datetime.now(ZoneInfo("America/Lima")),
            "type": "access"
        }

        return jwt.encode(
            payload,
            self.SECRET_KEY,
            algorithm="HS256"
        )

    def create_refresh_token(self, user: User) -> str:
        payload = {
            "user_id": str(user.id),
            "exp": datetime.now(ZoneInfo("America/Lima")) + timedelta(days=7),
            "iat": datetime.now(ZoneInfo("America/Lima")),
            "type": "refresh"
        }

        return jwt.encode(
            payload,
            self.SECRET_KEY,
            algorithm="HS256"
        )

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        try:
            payload = jwt.decode(
                refresh_token,
                self.SECRET_KEY,
                algorithms=["HS256"]
            )

            if payload.get("type") != "refresh":
                raise InvalidToken("Token inválido")

            new_payload = {
                "user_id": payload["user_id"],
                "email": payload.get("email"),
                "rol": payload.get("rol"),
                "exp": datetime.utcnow() + timedelta(minutes=15),
                "iat": datetime.utcnow(),
                "type": "access"
            }

            return jwt.encode(
                new_payload,
                self.SECRET_KEY,
                algorithm="HS256"
            )

        except jwt.ExpiredSignatureError:
            raise InvalidToken("Refresh token expirado")

        except jwt.InvalidTokenError:
            raise InvalidToken("Refresh token inválido")