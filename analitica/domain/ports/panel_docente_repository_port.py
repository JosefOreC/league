"""
Puerto (interfaz) del repositorio de Panel Docente.
El domain define el contrato; la infraestructura lo implementa.
No importa nada de application/ ni infrastructure/.
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..entities.panel_docente import CriterioConPercentil


class IPanelDocenteRepository(ABC):
    """
    Interfaz que todo repositorio concreto del panel docente debe implementar.
    Reutiliza la query de reporte-individual y agrega el cálculo de percentil.
    """

    @abstractmethod
    def obtener_criterios_con_percentil(
        self,
        torneo_id: str,
        equipo_id: str,
    ) -> list[CriterioConPercentil]:
        """
        Retorna los criterios del equipo con su posición percentil en el torneo.
        Reutiliza la infraestructura de reporte-individual, extendiéndola con
        el ranking percentílico por criterio.
        """
        ...

    @abstractmethod
    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        """Retorna el estado del torneo o None si no existe."""
        ...

    @abstractmethod
    def contar_partidos_finalizados(self, torneo_id: str) -> int:
        """
        Cuenta partidos finalized en el torneo (para validar PRELIMINAR).
        Se necesitan al menos 2 para emitir un panel PRELIMINAR.
        """
        ...

    @abstractmethod
    def equipo_pertenece_a_torneo(self, equipo_id: str, torneo_id: str) -> bool:
        """Verifica si el equipo está inscrito en el torneo."""
        ...

    @abstractmethod
    def obtener_docente_del_equipo(
        self, equipo_id: str
    ) -> Optional[tuple[str, str]]:
        """
        Retorna (docente_asesor_id, docente_nombre_completo) del equipo.
        Retorna None si el equipo no existe o no tiene docente asignado.
        """
        ...

    @abstractmethod
    def obtener_info_equipo_panel(
        self, torneo_id: str, equipo_id: str
    ) -> Optional[dict]:
        """
        Retorna datos base del equipo para el panel:
        torneo_nombre, equipo_nombre, posicion_final, medalla,
        puntaje_total_acumulado, total_partidos_jugados.
        """
        ...
