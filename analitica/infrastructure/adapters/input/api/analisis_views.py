"""
Controlador de Analítica — infrastructure/adapters/input/api/analisis_views.py
Capa: infrastructure/
Responsabilidad: parsear parámetros HTTP, llamar al use case, retornar respuesta JSON.
NO contiene lógica de negocio ni cálculos. NO hace try/catch para mapear a HTTP.
Las excepciones de dominio son manejadas por el exception_handler de esta vista.

Endpoints registrados aquí:
    GET /api/analitica/torneos/<torneo_id>/analisis-integral/   → HU-AN-01
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from authentication.infrastructure.security.auth_decorator import auth_required
from authentication.domain.value_objects.enum.system_rol import SystemRol

from .....domain.exceptions import (
    TorneoNoEncontradoException,
    TorneoNoFinalizadoException,
    SinResultadosDefinitivosException,
    AccesoNoAutorizadoException,
    EquipoNoEncontradoException,
    DocenteNoVinculadoException,
)
from .....infrastructure.repositories.analisis_integral_repository import (
    AnalisisIntegralRepositoryImpl,
)
from .....application.use_cases.obtener_analisis_integral_use_case import (
    ObtenerAnalisisIntegralUseCase,
)

# ── Excepción → código HTTP ────────────────────────────────────────────────────
EXCEPTION_HTTP_MAP = {
    TorneoNoEncontradoException: status.HTTP_404_NOT_FOUND,
    TorneoNoFinalizadoException: status.HTTP_409_CONFLICT,
    SinResultadosDefinitivosException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AccesoNoAutorizadoException: status.HTTP_403_FORBIDDEN,
    EquipoNoEncontradoException: status.HTTP_404_NOT_FOUND,
    DocenteNoVinculadoException: status.HTTP_403_FORBIDDEN,
}


def _handle_domain_exception(exc: Exception) -> Response:
    """Mapea excepciones de dominio a respuestas HTTP."""
    http_status = EXCEPTION_HTTP_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"error": str(exc)}, status=http_status)


def _analisis_integral_to_dict(analisis) -> dict:
    """Serializa la entidad AnalisisIntegral a dict JSON-serializable."""
    return {
        "torneo_id": analisis.torneo_id,
        "torneo_nombre": analisis.torneo_nombre,
        "categoria_filtrada": analisis.categoria_filtrada,
        "metricas_globales": {
            "total_equipos": analisis.total_equipos,
            "total_partidos": analisis.total_partidos,
            "puntaje_promedio_global": round(analisis.puntaje_promedio_global, 4),
            "desviacion_estandar_global": round(analisis.desviacion_estandar_global, 4),
            "puntaje_maximo": round(analisis.puntaje_maximo, 4),
            "puntaje_minimo": round(analisis.puntaje_minimo, 4),
        },
        "equipo_max": {
            "equipo_id": analisis.equipo_max.equipo_id,
            "nombre": analisis.equipo_max.nombre,
            "puntaje_total": round(analisis.equipo_max.puntaje_total, 4),
            "posicion_final": analisis.equipo_max.posicion_final,
            "medalla": analisis.equipo_max.medalla,
        },
        "equipo_min": {
            "equipo_id": analisis.equipo_min.equipo_id,
            "nombre": analisis.equipo_min.nombre,
            "puntaje_total": round(analisis.equipo_min.puntaje_total, 4),
            "posicion_final": analisis.equipo_min.posicion_final,
            "medalla": analisis.equipo_min.medalla,
        },
        "distribucion_criterios": [
            {
                "criterio_id": d.criterio_id,
                "criterio_nombre": d.criterio_nombre,
                "peso": round(d.peso, 4),
                "promedio": round(d.promedio, 4),
                "maximo": round(d.maximo, 4),
                "minimo": round(d.minimo, 4),
                "desviacion_estandar": round(d.desviacion_estandar, 4),
            }
            for d in analisis.distribucion_criterios
        ],
        "ranking_final": analisis.ranking_final,
    }


# ── HU-AN-01: Análisis Integral ────────────────────────────────────────────────

@api_view(["GET"])
#@auth_required([SystemRol.ADMIN, SystemRol.MANAGER])
def get_analisis_integral(request, torneo_id: str):
    """
    GET /api/analitica/torneos/<torneo_id>/analisis-integral/
    Query param opcional: ?categoria=PRIMARY|SECONDARY

    Tiempo de respuesta objetivo: < 2s.
    Requiere rol: ADMIN o MANAGER (organizador del torneo).
    """
    categoria = request.query_params.get("categoria", None)

    repo = AnalisisIntegralRepositoryImpl()
    use_case = ObtenerAnalisisIntegralUseCase(repo)

    try:
        analisis = use_case.execute(torneo_id=torneo_id, categoria=categoria)
    except (
        TorneoNoEncontradoException,
        TorneoNoFinalizadoException,
        SinResultadosDefinitivosException,
        AccesoNoAutorizadoException,
    ) as exc:
        return _handle_domain_exception(exc)
    except Exception as exc:
        return Response(
            {"error": "Error interno del servidor.", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(_analisis_integral_to_dict(analisis), status=status.HTTP_200_OK)
