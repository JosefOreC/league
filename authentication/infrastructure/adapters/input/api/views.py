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

user_repository = UserRepositoryPostgresql()
password_service = PasswordService()
jwt_service = JWTService()

# Create your views here.
@api_view(['POST'])
def login(request):
    fields_required = ['email', 'password']
    if not request.data or not all(field in request.data and request.data[field] for field in fields_required):
        missing_fields = [field for field in fields_required if field not in request.data or not request.data[field]]
        return Response({"error": f"Faltan campos requeridos: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
    login_use_case = LoginUseCase(user_repository, password_service, jwt_service)
    try:
        response = login_use_case.execute(**request.data)
    except InvalidCredentials as e:
        response = {"error": str(e)}
        return Response(response, status=status.HTTP_401_UNAUTHORIZED)
    except AccountLocked as e:
        response = {"error": str(e)}
        return Response(response, status=status.HTTP_423_LOCKED)
    except Exception as e:
        response = {"error": str(e)}
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def refresh(request):
    if not request.data or "refresh_token" not in request.data:
        return Response(
            {"error": "refresh_token es requerido"},
            status=status.HTTP_400_BAD_REQUEST
        )

    refresh_use_case = RefreshTokenUseCase(jwt_service)

    try:
        response = refresh_use_case.execute(
            request.data["refresh_token"]
        )

        return Response(response, status=status.HTTP_200_OK)

    except InvalidToken as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_401_UNAUTHORIZED
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def register(request):
    return Response({"error": "No implementado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def me(request):
    return JsonResponse({"error": "No implementado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def logout(request):
    return JsonResponse({"error": "No implementado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)