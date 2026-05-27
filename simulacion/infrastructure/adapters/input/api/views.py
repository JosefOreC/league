from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from authentication.infrastructure.security.auth_decorator import auth_required
from simulacion.application.use_cases.predecir_resultado import PredecirResultadoUseCase
from simulacion.application.use_cases.obtener_retos import ObtenerRetosUseCase
from simulacion.application.use_cases.analizar_programacion import AnalizarProgramacionUseCase
from simulacion.application.use_cases.analizar_componentes import AnalizarComponentesUseCase
from simulacion.infrastructure.persistence.simulacion_repository import SimulacionRepository
from simulacion.infrastructure.adapters.output.models import AnalisisEntrega
from .serializers import (
    PredecirInputSerializer, PredecirOutputSerializer,
    AnalizarProgramacionInputSerializer, AnalizarComponentesInputSerializer,
    AnalisisEntregaSerializer,
)


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


@api_view(['GET'])
@auth_required()
def obtener_retos(request, torneo_id):
    caso_filtro = request.query_params.get('caso')
    try:
        resultado = ObtenerRetosUseCase().ejecutar(torneo_id, caso_filtro)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    return Response(resultado)


@api_view(['POST'])
@auth_required()
def analizar_programacion(request):
    ser = AnalizarProgramacionInputSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        resultado = AnalizarProgramacionUseCase().ejecutar(**ser.validated_data)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    return Response(resultado, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@auth_required()
def analizar_componentes(request):
    ser = AnalizarComponentesInputSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        resultado = AnalizarComponentesUseCase().ejecutar(**ser.validated_data)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    return Response(resultado, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@auth_required()
def listar_analisis(request, participante_id, torneo_id):
    qs = AnalisisEntrega.objects.filter(
        participante_id=participante_id,
        torneo_id=torneo_id,
    ).order_by('-creado_en')
    return Response(AnalisisEntregaSerializer(qs, many=True).data)
