from abc import ABC, abstractmethod
from typing import List, Optional


class RetoAnalisisRepositoryPort(ABC):

    @abstractmethod
    def obtener_retos_del_torneo(self, torneo_id: str) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    def obtener_reto_con_criterios(self, reto_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def guardar_analisis(self, datos: dict):
        raise NotImplementedError
