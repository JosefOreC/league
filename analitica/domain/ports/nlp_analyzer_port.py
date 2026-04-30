from abc import ABC, abstractmethod
from ..entities.nlp_analysis import NLPAnalysis


class NLPAnalyzerPort(ABC):
    """
    Outbound port: defines the contract that any NLP adapter must fulfill.
    The use case depends only on this abstraction, never on the concrete impl.
    """

    @abstractmethod
    def analyze(self, text: str) -> NLPAnalysis:
        """
        Parse *text* and return a fully-populated NLPAnalysis entity.
        Implementations MUST NOT raise exceptions for missing/ambiguous data;
        they should encode uncertainty in the FieldExtraction.missing flag and
        confidence score.
        """
        ...
