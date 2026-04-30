from enum import Enum


class EstadoAnalisis(str, Enum):
    COMPLETO   = "COMPLETO"
    INCOMPLETO = "INCOMPLETO"
    AMBIGUO    = "AMBIGUO"
