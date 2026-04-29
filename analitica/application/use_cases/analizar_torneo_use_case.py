from ...domain.entities.nlp_analysis import NLPAnalysis
from ...domain.ports.nlp_analyzer_port import NLPAnalyzerPort
from ...domain.ports.nlp_analysis_repository_port import NLPAnalysisRepositoryPort


class AnalizarTorneoUseCase:

    def __init__(
        self,
        nlp_analyzer: NLPAnalyzerPort,
        repository: NLPAnalysisRepositoryPort,
    ) -> None:
        self._nlp_analyzer = nlp_analyzer
        self._repository = repository

    def execute(self, input_texto: str) -> NLPAnalysis:
        texto = (input_texto or "").strip()
        if not texto:
            raise ValueError("El texto de entrada no puede estar vacío")

        analysis = self._nlp_analyzer.analyze(texto)
        self._repository.save(analysis, texto)
        return analysis
