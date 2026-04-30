from decimal import Decimal

from ...domain.entities.criterio_ia import CriterioIA, validar_suma_pesos
from ...domain.ports.criterio_ia_repository_port import CriterioIARepositoryPort


class ActualizarPesoCriterioUseCase:

    def __init__(self, repository: CriterioIARepositoryPort) -> None:
        self._repository = repository

    def execute(
        self, criterio_id: str, nuevo_peso: float
    ) -> dict:
        """
        Actualiza el peso de un criterio y retorna la validación del conjunto.

        Retorna dict con: criterio actualizado, suma_actual, es_valida, mensaje.
        """
        criterio = self._repository.find_by_id(criterio_id)
        if criterio is None:
            raise ValueError(f"Criterio '{criterio_id}' no encontrado")

        criterio.actualizar_peso(nuevo_peso)
        self._repository.update(criterio)

        todos = self._repository.find_by_sesion(criterio.sesion_ia_id)
        es_valida, suma = validar_suma_pesos(todos)

        mensaje = None
        if not es_valida:
            mensaje = (
                f"La suma actual es {float(suma):.2f}%. "
                "Debe ajustar otros criterios para mantener el total en 100%."
            )

        return {
            "criterio":    criterio.to_dict(),
            "suma_actual": float(suma),
            "es_valida":   es_valida,
            "mensaje":     mensaje,
            "criterios":   [c.to_dict() for c in todos],
        }
