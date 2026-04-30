from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ....repositories.postgresql_repository.user_repository_postgresql import UserRepositoryPostgresql
from .....application.use_cases.login_use_case import LoginUseCase, InvalidCredentials, AccountLocked
from .....application.service.password_service import PasswordService
from .....application.service.jwt_service import JWTService, InvalidToken
from .....application.use_cases.refresh_token_use_case import RefreshTokenUseCase
from ....security.auth_decorator import auth_required
from .....application.service.auth_identity_service import AuthIdentityService
from .....application.use_cases.register_use_case import RegisterUseCase
from datetime import datetime

# Inicialización de repositorios y servicios
user_repository = UserRepositoryPostgresql()
password_service = PasswordService()
jwt_service = JWTService()
register_use_case = RegisterUseCase(user_repository, password_service)
auth_identity_service = AuthIdentityService(user_repository)

def _parse_date(value: str, field_name: str) -> datetime:
    """Helper para normalizar fechas provenientes de la petición."""
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(f"El campo '{field_name}' requiere formato YYYY-MM-DD")

@api_view(['POST'])
def login(request):
    fields_required = ['email', 'password']
    if not request.data or not all(field in request.data and request.data[field] for field in fields_required):
        missing_fields = [field for field in fields_required if field not in request.data or not request.data[field]]
        return Response({"error": f"Faltan campos requeridos: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    login_use_case = LoginUseCase(user_repository, password_service, jwt_service)
    try:
        response = login_use_case.execute(**request.data)
        return Response(response, status=status.HTTP_200_OK)
    except InvalidCredentials as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except AccountLocked as e:
        return Response({"error": str(e)}, status=status.HTTP_423_LOCKED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def refresh(request):
    """Renovación del token de acceso."""
    if not request.data or "refresh_token" not in request.data:
        return Response({"error": "refresh_token es requerido"}, status=status.HTTP_400_BAD_REQUEST)

    refresh_use_case = RefreshTokenUseCase(jwt_service)
    try:
        response = refresh_use_case.execute(request.data["refresh_token"])
        return Response(response, status=status.HTTP_200_OK)
    except InvalidToken as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def register(request):
    """Entry point para el registro de usuarios con soporte para roles dinámicos."""
    fields_required = ['email', 'password', 'name', 'birth_date']
    if not request.data or not all(field in request.data and request.data[field] for field in fields_required):
        return Response({"error": "Faltan campos requeridos"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = request.data.copy()
        data['birth_date'] = _parse_date(data['birth_date'], 'birth_date')
        register_use_case.execute(**data)
        return Response({"message": "Usuario creado exitosamente"}, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@auth_required()
def me(request):
    user = auth_identity_service.build_user_from_payload(request.user_data)
    return Response(user.to_external_dict(), status=status.HTTP_200_OK)

@api_view(['PUT'])
@auth_required()
def logout(request):
    return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)
