import uuid
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from ..value_objects.enums.tipo_dato import TipoDato
from ..value_objects.enums.estado_criterio import EstadoCriterio


@dataclass
class CriterioIA:
    id: str
    torneo_id: str
    sesion_ia_id: str
    nombre: str
    descripcion: str
    tipo_dato: TipoDato
    peso_porcentual: Decimal   # 0.01 – 100.00; suma del conjunto = 100.00
    mayor_es_mejor: bool
    orden: int
    estado: EstadoCriterio
    valor_minimo: Optional[Decimal] = None   # solo NUMERICO
    valor_maximo: Optional[Decimal] = None   # solo NUMERICO

    # ------------------------------------------------------------------ #
    # Factory                                                              #
    # ------------------------------------------------------------------ #

    @classmethod
    def create(
        cls,
        torneo_id: str,
        sesion_ia_id: str,
        nombre: str,
        descripcion: str,
        tipo_dato: TipoDato,
        peso_porcentual: float,
        mayor_es_mejor: bool,
        orden: int,
        valor_minimo: Optional[float] = None,
        valor_maximo: Optional[float] = None,
    ) -> "CriterioIA":
        nombre = nombre.strip()
        if not nombre or len(nombre) > 100:
            raise ValueError("El nombre debe tener entre 1 y 100 caracteres")

        peso = Decimal(str(peso_porcentual)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if peso <= 0 or peso > 100:
            raise ValueError("peso_porcentual debe estar entre 0.01 y 100.00")

        v_min = Decimal(str(valor_minimo)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if valor_minimo is not None else None
        v_max = Decimal(str(valor_maximo)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if valor_maximo is not None else None

        if tipo_dato == TipoDato.NUMERICO:
            if v_min is None or v_max is None:
                raise ValueError("valor_minimo y valor_maximo son obligatorios para tipo NUMERICO")
            if v_min >= v_max:
                raise ValueError("valor_minimo debe ser menor a valor_maximo")

        return cls(
            id=str(uuid.uuid4()),
            torneo_id=torneo_id,
            sesion_ia_id=sesion_ia_id,
            nombre=nombre,
            descripcion=descripcion,
            tipo_dato=tipo_dato,
            peso_porcentual=peso,
            mayor_es_mejor=mayor_es_mejor,
            orden=orden,
            estado=EstadoCriterio.SUGERIDO,
            valor_minimo=v_min,
            valor_maximo=v_max,
        )

    # ------------------------------------------------------------------ #
    # Comportamiento                                                       #
    # ------------------------------------------------------------------ #

    def actualizar_peso(self, nuevo_peso: float) -> "CriterioIA":
        """Retorna una nueva instancia con el peso actualizado y estado MODIFICADO."""
        peso = Decimal(str(nuevo_peso)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if peso <= 0 or peso > 100:
            raise ValueError("peso_porcentual debe estar entre 0.01 y 100.00")
        self.peso_porcentual = peso
        self.estado = EstadoCriterio.MODIFICADO
        return self

    def aceptar(self) -> None:
        self.estado = EstadoCriterio.ACEPTADO

    def rechazar(self) -> None:
        self.estado = EstadoCriterio.RECHAZADO

    # ------------------------------------------------------------------ #
    # Serialización                                                        #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "torneo_id":        self.torneo_id,
            "sesion_ia_id":     self.sesion_ia_id,
            "nombre":           self.nombre,
            "descripcion":      self.descripcion,
            "tipo_dato":        self.tipo_dato.value,
            "peso_porcentual":  float(self.peso_porcentual),
            "valor_minimo":     float(self.valor_minimo) if self.valor_minimo is not None else None,
            "valor_maximo":     float(self.valor_maximo) if self.valor_maximo is not None else None,
            "mayor_es_mejor":   self.mayor_es_mejor,
            "orden":            self.orden,
            "estado":           self.estado.value,
        }


# ------------------------------------------------------------------ #
# Validación de conjunto                                              #
# ------------------------------------------------------------------ #

def validar_suma_pesos(criterios: list[CriterioIA]) -> tuple[bool, Decimal]:
    """Retorna (es_valida, suma_actual). Tolerancia ±0.01 sobre 100.00."""
    if not criterios:
        return False, Decimal("0.00")
    suma = sum(c.peso_porcentual for c in criterios).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return abs(suma - Decimal("100.00")) <= Decimal("0.01"), suma
