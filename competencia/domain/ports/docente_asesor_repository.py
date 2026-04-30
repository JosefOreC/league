from abc import ABC, abstractmethod
from ..entities.docente_asesor import DocenteAsesor

class DocenteAsesorRepository(ABC):
    @abstractmethod
    def save(self, docente: DocenteAsesor):
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> DocenteAsesor | None:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> DocenteAsesor | None:
        pass
