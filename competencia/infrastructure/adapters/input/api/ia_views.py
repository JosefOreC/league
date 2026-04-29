from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from authentication.domain.value_objects.enum.system_rol import SystemRol
from .....infrastructure.security.auth_decorator import auth_required

from .....application.use_cases.analizar_torneo_use_case import AnalizarTorneoUseCase
from .....infrastructure.ia.rules_nlp_adapter import RulesBasedNLPAdapter
from .....infrastructure.repositories.nlp_analysis_repository import NLPAnalysisRepository

from .....application.use_cases.generar_criterios_ia_use_case import GenerarCriteriosIAUseCase
from .....application.use_cases.actualizar_peso_criterio_use_case import ActualizarPesoCriterioUseCase
from .....application.use_cases.confirmar_criterios_ia_use_case import (
    ConfirmarCriteriosIAUseCase,
    SumaPesosInvalidaError,
)
from .....infrastructure.ia.rubrica_generator import RubricaGenerator
from .....infrastructure.repositories.criterio_ia_repository import CriterioIARepository


# ──────────────────────────────────────────────────────────────────────────────
# HU-IA-01 — Análisis NLP
# ──────────────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def analizar_torneo(request):
    """
    POST /api/ia/analizar
    Body: { "texto": "<descripción libre del torneo>" }
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


# ──────────────────────────────────────────────────────────────────────────────
# HU-IA-05 — Generación de Criterios (Rúbricas)
# ──────────────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def generar_criterios(request):
    """
    POST /api/ia/generar-criterios
    Body: {
        "torneo_id":   "<uuid>",
        "tipo_torneo": "KNOCKOUT | ROUND_ROBIN | HYBRID",
        "nivel":       "BASICO | INTERMEDIO | AVANZADO"  (o 1 / 2 / 3),
        "categoria":   "PRIMARY | SECONDARY"
    }
    Genera entre 3-10 criterios de evaluación con suma de pesos = 100%.
    """
    data = request.data or {}
    required = ["torneo_id", "tipo_torneo", "nivel", "categoria"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return Response(
            {"error": f"Faltan campos requeridos: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        use_case = GenerarCriteriosIAUseCase(
            generator=RubricaGenerator(),
            repository=CriterioIARepository(),
        )
        sesion_id, criterios = use_case.execute(
            torneo_id=str(data["torneo_id"]),
            tipo_torneo=str(data["tipo_torneo"]),
            nivel=data["nivel"],
            categoria=str(data["categoria"]),
        )
        return Response(
            {
                "sesion_ia_id": sesion_id,
                "criterios":    [c.to_dict() for c in criterios],
                "total_pesos":  sum(c.peso_porcentual for c in criterios),
            },
            status=status.HTTP_200_OK,
        )

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def actualizar_peso_criterio(request, criterio_id: str):
    """
    PUT /api/ia/criterios/<criterio_id>
    Body: { "peso_porcentual": <float> }

    Actualiza el peso de un criterio y retorna la suma del conjunto
    junto con una alerta si la suma ≠ 100%.
    """
    data = request.data or {}
    if "peso_porcentual" not in data:
        return Response(
            {"error": "El campo 'peso_porcentual' es requerido"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        resultado = ActualizarPesoCriterioUseCase(
            repository=CriterioIARepository()
        ).execute(
            criterio_id=criterio_id,
            nuevo_peso=float(data["peso_porcentual"]),
        )
        return Response(resultado, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def confirmar_criterios(request, sesion_ia_id: str):
    """
    POST /api/ia/criterios/<sesion_ia_id>/confirmar

    Confirma (acepta) todos los criterios de la sesión si la suma = 100%.
    Retorna HTTP 422 si la suma ≠ 100%.
    """
    try:
        criterios = ConfirmarCriteriosIAUseCase(
            repository=CriterioIARepository()
        ).execute(sesion_ia_id=sesion_ia_id)
        return Response({"criterios": criterios}, status=status.HTTP_200_OK)

    except SumaPesosInvalidaError as e:
        return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
