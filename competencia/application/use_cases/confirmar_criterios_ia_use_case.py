from ...domain.entities.criterio_ia import validar_suma_pesos
from ...domain.ports.criterio_ia_repository_port import CriterioIARepositoryPort


class ConfirmarCriteriosIAUseCase:
    """
    Confirma los criterios de una sesión IA si y solo si la suma de pesos = 100%.
    Lanza SumaPesosInvalidaError (422) en caso contrario.
    """

    def __init__(self, repository: CriterioIARepositoryPort) -> None:
        self._repository = repository

    def execute(self, sesion_ia_id: str) -> list[dict]:
        criterios = self._repository.find_by_sesion(sesion_ia_id)
        if not criterios:
            raise ValueError(f"No se encontraron criterios para la sesión '{sesion_ia_id}'")

        es_valida, suma = validar_suma_pesos(criterios)
        if not es_valida:
            raise SumaPesosInvalidaError(
                f"La suma de pesos porcentuales debe ser exactamente 100.00%. "
                f"Suma actual: {float(suma):.2f}%"
            )

        for c in criterios:
            c.aceptar()
        self._repository.update_all(criterios)

        return [c.to_dict() for c in criterios]


class SumaPesosInvalidaError(Exception):
    pass
