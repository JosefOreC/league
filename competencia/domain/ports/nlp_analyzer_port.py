from abc import ABC, abstractmethod
from ..entities.nlp_analysis import NLPAnalysis


class NLPAnalyzerPort(ABC):
    """
    Outbound port: contrato que debe cumplir cualquier adaptador NLP.
    Las implementaciones NO deben lanzar excepciones por datos faltantes;
    deben reflejar la incertidumbre en FieldExtraction.missing y confidence.
    """

    @abstractmethod
    def analyze(self, text: str) -> NLPAnalysis: ...
