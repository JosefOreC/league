"""
Excepciones tipadas del dominio de Analítica.
El ExceptionFilter de infraestructura mapea estas a códigos HTTP.
No hagas try/catch en los controladores para mapear a HTTP manualmente.

Mapeo esperado:
    TorneoNoFinalizadoException      → 409 Conflict
    SinResultadosDefinitivosException → 422 Unprocessable Entity
    AccesoNoAutorizadoException      → 403 Forbidden
    TorneoNoEncontradoException      → 404 Not Found
    EquipoNoEncontradoException      → 404 Not Found
"""


class TorneoNoFinalizadoException(Exception):
    """Se lanza cuando el torneo no está en estado FINISHED y la operación lo requiere."""
    def __init__(self, torneo_id: str, estado_actual: str):
        super().__init__(
            f"El torneo '{torneo_id}' debe estar en estado FINISHED. Estado actual: '{estado_actual}'."
        )
        self.torneo_id = torneo_id
        self.estado_actual = estado_actual


class SinResultadosDefinitivosException(Exception):
    """Se lanza cuando el torneo no tiene resultados en estado DEFINITIVO."""
    def __init__(self, torneo_id: str):
        super().__init__(
            f"El torneo '{torneo_id}' no tiene resultados con estado DEFINITIVO."
        )
        self.torneo_id = torneo_id


class AccesoNoAutorizadoException(Exception):
    """Se lanza cuando el usuario no tiene el rol requerido para la operación."""
    def __init__(self, detalle: str = "No tiene permisos para esta operación."):
        super().__init__(detalle)


class TorneoNoEncontradoException(Exception):
    """Se lanza cuando el torneo no existe en la BD."""
    def __init__(self, torneo_id: str):
        super().__init__(f"Torneo con id '{torneo_id}' no encontrado.")
        self.torneo_id = torneo_id


class EquipoNoEncontradoException(Exception):
    """Se lanza cuando el equipo no existe o no pertenece al torneo indicado."""
    def __init__(self, equipo_id: str, torneo_id: str = None):
        msg = f"Equipo con id '{equipo_id}' no encontrado"
        if torneo_id:
            msg += f" en el torneo '{torneo_id}'"
        super().__init__(msg + ".")
        self.equipo_id = equipo_id
        self.torneo_id = torneo_id


class DocenteNoVinculadoException(Exception):
    """Se lanza cuando el docente asesor no está vinculado al equipo indicado."""
    def __init__(self, docente_id: str, equipo_id: str):
        super().__init__(
            f"El docente asesor '{docente_id}' no está vinculado al equipo '{equipo_id}'."
        )
        self.docente_id = docente_id
        self.equipo_id = equipo_id
