from abc import ABC, abstractmethod
from typing import Optional
from ..entities.certificado_digital import CertificadoDigital, DatosParticipante, DatosGanador


class ICertificadosRepository(ABC):

    @abstractmethod
    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        """Retorna el state del torneo o None si no existe."""
        ...

    @abstractmethod
    def obtener_participantes(self, torneo_id: str) -> list[DatosParticipante]:
        """
        Una sola query: todos los participantes de equipos APROBADO en el torneo,
        con datos de equipo, institución y torneo.
        Ordenados por equipo + apellido.
        """
        ...

    @abstractmethod
    def obtener_datos_ganador(
        self, torneo_id: str, equipo_id: str
    ) -> Optional[DatosGanador]:
        """
        Datos del equipo desde final_ranking + participantes del equipo.
        Retorna None si el equipo no tiene medalla ORO en el torneo.
        """
        ...

    @abstractmethod
    def guardar_certificado(
        self,
        torneo_id: str,
        tipo_certificado: str,
        nombres_destinatario: str,
        institucion: str,
        codigo_verificacion: str,
        participante_id: Optional[str],
        equipo_id: Optional[str],
        posicion_final: Optional[int],
        medalla: Optional[str],
    ) -> CertificadoDigital:
        ...
