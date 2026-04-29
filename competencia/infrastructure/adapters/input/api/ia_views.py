from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from authentication.domain.value_objects.enum.system_rol import SystemRol
from .....infrastructure.security.auth_decorator import auth_required
from .....application.use_cases.analizar_torneo_use_case import AnalizarTorneoUseCase
from .....infrastructure.ia.rules_nlp_adapter import RulesBasedNLPAdapter
from .....infrastructure.repositories.nlp_analysis_repository import NLPAnalysisRepository


@api_view(["POST"])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def analizar_torneo(request):
    """
    POST /api/ia/analizar
    Body: { "texto": "<descripción libre del torneo>" }

    Extrae entidades NLP: numero_equipos, categoria, nivel_tecnico,
    tipo_torneo_sugerido con nivel de confianza por campo (0.0–1.0).
    """
    texto = (request.data or {}).get("texto", "")

    if not texto or not str(texto).strip():
        return Response(
            {"error": "El campo 'texto' es requerido y no puede estar vacío"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        use_case = AnalizarTorneoUseCase(
            nlp_analyzer=RulesBasedNLPAdapter(),
            repository=NLPAnalysisRepository(),
        )
        analysis = use_case.execute(str(texto))
        return Response(analysis.to_dict(), status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
