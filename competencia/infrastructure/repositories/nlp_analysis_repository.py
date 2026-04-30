from ...domain.entities.nlp_analysis import NLPAnalysis
from ...domain.ports.nlp_analysis_repository_port import NLPAnalysisRepositoryPort


class NLPAnalysisRepository(NLPAnalysisRepositoryPort):

    def save(self, analysis: NLPAnalysis, input_texto: str) -> None:
        from ..adapters.output.models import NLPAnalysisModel

        def _enum_val(fe_value) -> str | None:
            if fe_value is None:
                return None
            return fe_value.value if hasattr(fe_value, "value") else str(fe_value)

        NLPAnalysisModel.objects.create(
            input_texto=input_texto,
            numero_equipos=analysis.numero_equipos.value,
            categoria=_enum_val(analysis.categoria.value),
            nivel_tecnico=_enum_val(analysis.nivel_tecnico.value),
            tipo_torneo_sugerido=_enum_val(analysis.tipo_torneo_sugerido.value),
            nombre_torneo=analysis.nombre.value,
            fecha_inicio_sugerida=analysis.fecha_inicio.value,
            fecha_fin_sugerida=analysis.fecha_fin.value,
            descripcion_sugerida=analysis.descripcion.value,
            intencion_usuario=analysis.intencion_usuario,
            nivel_confianza={
                "numero_equipos":       analysis.numero_equipos.confidence,
                "categoria":            analysis.categoria.confidence,
                "nivel_tecnico":        analysis.nivel_tecnico.confidence,
                "tipo_torneo_sugerido": analysis.tipo_torneo_sugerido.confidence,
                "nombre":               analysis.nombre.confidence,
                "fecha_inicio":         analysis.fecha_inicio.confidence,
                "fecha_fin":            analysis.fecha_fin.confidence,
                "descripcion":          analysis.descripcion.confidence,
            },
            estado_analisis=analysis.estado_analisis.value,
            campos_faltantes=analysis.campos_faltantes,
        )
