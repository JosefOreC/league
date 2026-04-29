from enum import Enum


class TipoTorneo(str, Enum):
    KNOCKOUT    = "KNOCKOUT"
    ROUND_ROBIN = "ROUND_ROBIN"
    HYBRID      = "HYBRID"
