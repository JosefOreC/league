"""
Value Object: CriterionScore — HU-SIM-02.

Representa el resultado de calificación simulada para un único criterio.
Es inmutable (frozen dataclass) y no conoce la base de datos.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CriterionScore:
    """
    Calificación simulada de un criterio de evaluación.

    Attributes:
        criterio_id:        PK del CriteriaModel.
        nombre:             Nombre del criterio.
        peso:               Peso porcentual del criterio en el torneo (0-100).
        valor_simulado:     Puntuación bruta dentro de [min_qualification, max_qualification].
        valor_normalizado:  Porcentaje de aprovechamiento del rango (0-100).
                            = (valor_simulado - min_q) / (max_q - min_q) * 100
        en_rango:           True si valor_simulado ∈ [min_qualification, max_qualification].
    """
    criterio_id: str
    nombre: str
    peso: float
    valor_simulado: float
    valor_normalizado: float
    en_rango: bool
