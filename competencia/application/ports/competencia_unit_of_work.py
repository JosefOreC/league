from abc import ABC, abstractmethod

class CompetenciaUnitOfWork(ABC):

    @property
    @abstractmethod
    def tournaments(self):
        pass

    @property
    @abstractmethod
    def teams(self):
        pass

    @property
    @abstractmethod
    def tournament_teams(self):
        pass

    @property
    @abstractmethod
    def institutions(self):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass

    @abstractmethod
    async def __aenter__(self):
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass