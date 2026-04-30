from dataclasses import dataclass, field
from typing import Optional
from ..value_objects.enums.categoria import Categoria
from ..value_objects.enums.nivel_tecnico import NivelTecnico
from ..value_objects.enums.tipo_torneo import TipoTorneo
from ..value_objects.enums.estado_analisis import EstadoAnalisis


@dataclass(frozen=True)
class FieldExtraction:
    value: Optional[object]
    confidence: float  # 0.0 – 1.0
    missing: bool = False


@dataclass(frozen=True)
class NLPAnalysis:
    numero_equipos: FieldExtraction
    categoria: FieldExtraction
    nivel_tecnico: FieldExtraction
    tipo_torneo_sugerido: FieldExtraction
    intencion_usuario: str
    estado_analisis: EstadoAnalisis
    campos_faltantes: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        def _serialize(fe: FieldExtraction) -> dict:
            v = fe.value
            if hasattr(v, "value"):
                v = v.value
            return {"value": v, "confidence": fe.confidence, "missing": fe.missing}

        fields = {
            "numero_equipos":       self.numero_equipos,
            "categoria":            self.categoria,
            "nivel_tecnico":        self.nivel_tecnico,
            "tipo_torneo_sugerido": self.tipo_torneo_sugerido,
        }

        return {
            **{name: _serialize(fe) for name, fe in fields.items()},
            "nivel_confianza":  {name: fe.confidence for name, fe in fields.items()},
            "intencion_usuario": self.intencion_usuario,
            "estado_analisis":   self.estado_analisis.value,
            "campos_faltantes":  self.campos_faltantes,
            "advertencias":      self.advertencias,
        }
