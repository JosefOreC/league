from enum import Enum


class EstadoCriterio(str, Enum):
    SUGERIDO   = "SUGERIDO"
    ACEPTADO   = "ACEPTADO"
    MODIFICADO = "MODIFICADO"
    RECHAZADO  = "RECHAZADO"
