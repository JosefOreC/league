"""
Controlador de Analítica — infrastructure/adapters/input/api/analisis_views.py
Capa: infrastructure/
Responsabilidad: parsear parámetros HTTP, llamar al use case, retornar respuesta JSON.
NO contiene lógica de negocio ni cálculos.
Las excepciones de dominio son mapeadas a HTTP mediante EXCEPTION_HTTP_MAP.

Endpoints:
    GET /api/analitica/torneos/<torneo_id>/analisis-integral/                      → HU-AN-01
    GET /api/analitica/torneos/<torneo_id>/equipos/<equipo_id>/reporte-individual/ → HU-AN-02
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
from .....infrastructure.repositories.reporte_individual_repository import (
    ReporteIndividualRepositoryImpl,
)
from .....application.use_cases.generar_reporte_individual_use_case import (
    GenerarReporteIndividualUseCase,
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

DOMAIN_EXCEPTIONS = tuple(EXCEPTION_HTTP_MAP.keys())


def _handle_domain_exception(exc: Exception) -> Response:
    """Mapea excepciones de dominio a respuestas HTTP."""
    http_status = EXCEPTION_HTTP_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"error": str(exc)}, status=http_status)


# ── Serializadores ─────────────────────────────────────────────────────────────

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


def _reporte_individual_to_dict(reporte) -> dict:
    """Serializa la entidad ReporteIndividual a dict JSON-serializable."""
    return {
        "torneo_id": reporte.torneo_id,
        "torneo_nombre": reporte.torneo_nombre,
        "equipo": {
            "equipo_id": reporte.equipo_id,
            "nombre": reporte.equipo_nombre,
            "categoria": reporte.categoria,
            "institucion": reporte.institucion_nombre,
            "posicion_final": reporte.posicion_final,
            "medalla": reporte.medalla,
        },
        "resumen": {
            "total_partidos_jugados": reporte.total_partidos_jugados,
            "victorias": reporte.victorias,
            "derrotas": reporte.derrotas,
            "puntaje_total_acumulado": reporte.puntaje_total_acumulado,
            "promedio_puntaje_torneo": reporte.promedio_puntaje_torneo,
            "comparativa_vs_promedio_torneo_pct": reporte.comparativa_vs_promedio_torneo,
        },
        "partidos": [
            {
                "partido_id": p.partido_id,
                "ronda": p.ronda,
                "rival_id": p.rival_id,
                "rival_nombre": p.rival_nombre,
                "puntaje_equipo": p.puntaje_equipo,
                "puntaje_rival": p.puntaje_rival,
                "ganador_id": p.ganador_id,
                "es_victoria": p.es_victoria,
                "fecha_programada": p.fecha_programada,
            }
            for p in reporte.partidos
        ],
        "detalle_criterios": [
            {
                "criterio_id": c.criterio_id,
                "criterio_nombre": c.criterio_nombre,
                "peso": c.peso,
                "promedio_equipo": c.promedio_equipo,
                "maximo_equipo": c.maximo_equipo,
                "minimo_equipo": c.minimo_equipo,
                "promedio_torneo": c.promedio_torneo,
                "comparativa_vs_promedio_pct": c.comparativa_vs_promedio,
            }
            for c in reporte.detalle_criterios
        ],
        "evolucion_por_ronda": [
            {
                "ronda": e.ronda,
                "puntaje_ronda": e.puntaje_ronda,
                "puntaje_acumulado": e.puntaje_acumulado,
            }
            for e in reporte.evolucion_por_ronda
        ],
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
    except DOMAIN_EXCEPTIONS as exc:
        return _handle_domain_exception(exc)
    except Exception as exc:
        return Response(
            {"error": "Error interno del servidor.", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(_analisis_integral_to_dict(analisis), status=status.HTTP_200_OK)


# ── HU-AN-02: Reporte de Desempeño Individual por Equipo ──────────────────────

@api_view(["GET"])
#@auth_required()
def get_reporte_individual(request, torneo_id: str, equipo_id: str):
    """
    GET /api/analitica/torneos/<torneo_id>/equipos/<equipo_id>/reporte-individual/
    Query param opcional: ?formato=PDF

    Requiere rol: representante o docente_asesor del equipo (o ADMIN/MANAGER).
    Si ?formato=PDF retorna { "mensaje": "PDF en construcción", "data": <JSON> }.
    El PDF real es tarea de HU-AN-06.
    """
    formato = request.query_params.get("formato", "").upper()

    # Extraer identidad del usuario del token JWT (cuando el decorador está activo)
    user_data = getattr(request, "user_data", {})
    usuario_id = user_data.get("user_id", "")
    usuario_rol = user_data.get("rol", "admin")  # Default permisivo sin auth activo

    repo = ReporteIndividualRepositoryImpl()
    use_case = GenerarReporteIndividualUseCase(repo)

    try:
        reporte = use_case.execute(
            torneo_id=torneo_id,
            equipo_id=equipo_id,
            usuario_id=usuario_id,
            usuario_rol=usuario_rol,
        )
    except DOMAIN_EXCEPTIONS as exc:
        return _handle_domain_exception(exc)
    except Exception as exc:
        return Response(
            {"error": "Error interno del servidor.", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = _reporte_individual_to_dict(reporte)

    if formato == "PDF":
        return Response(
            {"mensaje": "PDF en construcción", "data": data},
            status=status.HTTP_200_OK,
        )

    return Response(data, status=status.HTTP_200_OK)
