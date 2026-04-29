from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from authentication.application.service.jwt_service import JWTService
from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState
from authentication.application.service.auth_identity_service import AuthIdentityService


def auth_required(allowed_roles: list[SystemRol] = None):
    """
    Verifica JWT personalizado y permisos por rol.
    
    Usage:
        @auth_required()
        @auth_required([SystemRol.ADMIN])
        @auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return Response(
                    {"error": "Token de autenticación requerido"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            token = auth_header.split(" ")[1]

            jwt_service = JWTService()

            try:
                payload = jwt_service.verify_token(token)

                # Validar tipo
                if payload.get("type") != "access":
                    return Response(
                        {"error": "Token de acceso inválido"},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Adjuntar payload al request
                request.user_data = payload

                return view_func(request, *args, **kwargs)

            except ValueError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            except Exception as e:
                return Response(
                    {"error": "Error de autenticación", "detail": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return wrapper
    return decorator