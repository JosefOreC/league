from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from authentication.infrastructure.security.auth_decorator import auth_required
from simulacion.application.use_cases.predecir_resultado import PredecirResultadoUseCase
from simulacion.application.use_cases.obtener_retos import ObtenerRetosUseCase
from simulacion.application.use_cases.analizar_programacion import AnalizarProgramacionUseCase
from simulacion.application.use_cases.analizar_componentes import AnalizarComponentesUseCase
from simulacion.application.use_cases.ejecutar_simulacion import EjecutarSimulacionUseCase
from simulacion.infrastructure.persistence.simulacion_repository import (
    SimulacionRepository, obtener_contexto_torneo,
)
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


@api_view(['GET'])
@auth_required()
def contexto_torneo(request, tournament_id):
    user_id = request.user_data['user_id']
    try:
        ctx = obtener_contexto_torneo(tournament_id, user_id)
    except PermissionError as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

    # Reshape flat dict → nested structure expected by SimulationContext (frontend)
    payload = {
        'tournament': {
            'id':       tournament_id,
            'name':     ctx['torneo_nombre'],
            'state':    ctx.get('torneo_estado', ''),
            'category': ctx.get('category', ''),
        },
        'team': {
            'id':                      ctx['equipo_id'],
            'name':                    ctx.get('equipo_nombre', ctx['equipo_id']),
            'nivel_tecnico_declarado': ctx.get('nivel_tecnico', ''),
            'participants_count':      ctx.get('total_equipos', 0),
        },
        'criterios': [
            {
                'id':               c['criterio_id'],
                'name':             c['criterio_nombre'],
                'description':      c.get('criterio_descripcion', ''),
                'peso':             c['peso']*100,
                'min_qualification': c['min_value_qualification'],
                'max_qualification': c['max_value_qualification'],
            }
            for c in ctx['criterios']
        ],
    }
    return Response(payload)


@api_view(['POST'])
@auth_required()
def ejecutar_simulacion(request, tournament_id):
    entregable = request.data.get('entregable')

    if not entregable or not str(entregable).strip():
        return Response(
            {'campo': 'entregable', 'error': 'requerido'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(str(entregable).strip()) < 100:
        return Response(
            {
                'error':         'El entregable debe tener al menos 100 caracteres',
                'actual_length': len(str(entregable).strip()),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_id = request.user_data['user_id']
    try:
        resultado = EjecutarSimulacionUseCase().ejecutar(
            tournament_id=tournament_id,
            user_id=user_id,
            entregable=str(entregable),
        )
    except PermissionError as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

    return Response(resultado, status=status.HTTP_200_OK)
