from ..service.jwt_service import JWTService

class RefreshTokenUseCase:
    def __init__(self, jwt_service: JWTService):
        self.__jwt_service = jwt_service

    def execute(self, refresh_token: str) -> dict:
        new_access_token = self.__jwt_service.refresh_access_token(refresh_token)

        return {
            "access_token": new_access_token
        }