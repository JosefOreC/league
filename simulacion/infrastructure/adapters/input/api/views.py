from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from authentication.infrastructure.security.auth_decorator import auth_required
from simulacion.application.use_cases.predecir_resultado import PredecirResultadoUseCase
from simulacion.infrastructure.persistence.simulacion_repository import SimulacionRepository
from .serializers import PredecirInputSerializer, PredecirOutputSerializer


@api_view(['POST'])
@auth_required()
def predecir_resultado(request):
    ser = PredecirInputSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    use_case = PredecirResultadoUseCase()
    try:
        resultado = use_case.ejecutar(ser.validated_data)
    except RuntimeError as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(PredecirOutputSerializer(resultado).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@auth_required()
def historial_simulacion(request, participante_id: int):
    repo = SimulacionRepository()
    historial = repo.obtener_historial(participante_id)
    return Response(historial, status=status.HTTP_200_OK)
