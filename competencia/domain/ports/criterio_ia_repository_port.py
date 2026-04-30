from abc import ABC, abstractmethod
from ..entities.criterio_ia import CriterioIA


class CriterioIARepositoryPort(ABC):

    @abstractmethod
    def save_all(self, criterios: list[CriterioIA]) -> None: ...

    @abstractmethod
    def find_by_sesion(self, sesion_ia_id: str) -> list[CriterioIA]: ...

    @abstractmethod
    def find_by_id(self, criterio_id: str) -> CriterioIA | None: ...

    @abstractmethod
    def update(self, criterio: CriterioIA) -> None: ...

    @abstractmethod
    def update_all(self, criterios: list[CriterioIA]) -> None: ...
