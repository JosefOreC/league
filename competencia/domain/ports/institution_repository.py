from abc import ABC, abstractmethod
from ..entities.institution import Institution

class InstitutionRepository(ABC):
    @abstractmethod
    def save(self, institution: Institution):
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> Institution | None:
        pass
    
    @abstractmethod
    def find_all(self) -> list[Institution]:
        pass
    
    @abstractmethod
    def delete(self, id: str):
        pass
    
    @abstractmethod
    def update(self, institution: Institution):
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Institution | None:
        pass
    
    @abstractmethod
    def find_by_city(self, city: str) -> list[Institution]:
        pass
    