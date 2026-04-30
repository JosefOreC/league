from abc import ABC, abstractmethod
from ..entities.nlp_analysis import NLPAnalysis


class NLPAnalysisRepositoryPort(ABC):

    @abstractmethod
    def save(self, analysis: NLPAnalysis, input_texto: str) -> None: ...
