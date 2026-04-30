from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.infrastructure.security.auth_decorator import auth_required

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

from ...output.models import TournamentModel
import uuid as _uuid
import random


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
            descripcion=str(data.get("descripcion", "")),
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


# ──────────────────────────────────────────────────────────────────────────────
# HU-IA-02 — Recomendación de Dificultad
# ──────────────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def recomendar_dificultad(request):
    """
    POST /api/ia/recomendar-dificultad
    Body: { "torneo_id": "<uuid>" }
    """
    torneo_id = (request.data or {}).get("torneo_id")
    if not torneo_id:
        return Response({"error": "torneo_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        torneo = TournamentModel.objects.get(id=torneo_id)
        # Lógica simple: Primary -> 2, Secondary -> 4, +1 si hay muchos equipos
        nivel = 2 if torneo.category.upper() == "EXPLORADOR" or torneo.category.upper() == "PRIMARY" else 4
        
        return Response({
            "sesion_ia_id": str(_uuid.uuid4()),
            "nivel_recomendado": nivel,
            "nivel_confianza": 0.85,
            "justificacion": f"Basado en la categoría {torneo.category} y el alcance del torneo.",
            "alertas": []
        }, status=status.HTTP_200_OK)
    except TournamentModel.DoesNotExist:
        return Response({"error": "Torneo no encontrado"}, status=status.HTTP_404_NOT_FOUND)


# ──────────────────────────────────────────────────────────────────────────────
# HU-IA-03 — Recomendación de Formato
# ──────────────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def recomendar_formato(request):
    """
    POST /api/ia/recomendar-formato
    Body: { "torneo_id": "<uuid>", "objetivo_declarado": "...", "tiempo_disponible_dias": 1 }
    """
    data = request.data or {}
    torneo_id = data.get("torneo_id")
    if not torneo_id:
        return Response({"error": "torneo_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        torneo = TournamentModel.objects.get(id=torneo_id)
        # Lógica: Pocos equipos -> Knockout, Muchos -> Hybrid, Intermedio -> Round Robin
        # (Usamos 8 y 16 como umbrales arbitrarios para esta versión basada en reglas)
        formato = "knockout"
        config = {"seed_enabled": True, "third_place": True, "best_of": 3}
        
        # Intentar obtener max_teams de las reglas si existen
        max_teams = 8
        if hasattr(torneo, 'tournament_rule'):
            max_teams = torneo.tournament_rule.max_teams

        if max_teams > 12:
            formato = "hybrid"
            config = {"teams_for_group": 4, "classified_by_group": 2, "num_rounds": 1, "third_place": False, "final_format": "KNOCKOUT"}
        elif max_teams > 6:
            formato = "round_robin"
            config = {"num_rounds": 1, "point_to_victory": 3, "point_to_draw": 1, "point_to_defeat": 0, "tie_breaking_criteria": ["DIFF_POINTS"]}

        return Response({
            "sesion_ia_id": str(_uuid.uuid4()),
            "torneo_id": torneo_id,
            "formato_recomendado": formato,
            "config_sugerida": config,
            "justificacion": f"Se recomienda {formato} para optimizar la experiencia de los {max_teams} equipos previstos.",
            "nivel_confianza": 0.9
        }, status=status.HTTP_200_OK)
    except TournamentModel.DoesNotExist:
        return Response({"error": "Torneo no encontrado"}, status=status.HTTP_404_NOT_FOUND)


# ──────────────────────────────────────────────────────────────────────────────
# HU-IA-04 — Generación de Reglas Operativas
# ──────────────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def generar_reglas_operativas(request):
    """
    POST /api/ia/generar-reglas
    Body: { "torneo_id": "<uuid>" }
    """
    torneo_id = (request.data or {}).get("torneo_id")
    if not torneo_id:
        return Response({"error": "torneo_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        TournamentModel.objects.get(id=torneo_id)
        sesion_id = str(_uuid.uuid4())
        
        reglas = [
            {
                "torneo_id": torneo_id,
                "sesion_ia_id": sesion_id,
                "nombre": "Tiempo de Ronda",
                "descripcion": "Duración máxima de cada intento o partida.",
                "valor": "180",
                "unidad": "segundos",
                "categoria_regla": "TIEMPO",
                "nivel_aplicable": 1,
                "estado": "SUGERIDA"
            },
            {
                "torneo_id": torneo_id,
                "sesion_ia_id": sesion_id,
                "nombre": "Peso Máximo del Robot",
                "descripcion": "El robot no debe exceder este peso para ser elegible.",
                "valor": "1.5",
                "unidad": "kg",
                "categoria_regla": "PESO",
                "nivel_aplicable": 1,
                "estado": "SUGERIDA"
            },
            {
                "torneo_id": torneo_id,
                "sesion_ia_id": sesion_id,
                "nombre": "Dimensiones Máximas",
                "descripcion": "El robot debe caber en un cubo de estas dimensiones.",
                "valor": "25x25x25",
                "unidad": "cm",
                "categoria_regla": "DIMENSION",
                "nivel_aplicable": 1,
                "estado": "SUGERIDA"
            }
        ]
        
        return Response(reglas, status=status.HTTP_200_OK)
    except TournamentModel.DoesNotExist:
        return Response({"error": "Torneo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
