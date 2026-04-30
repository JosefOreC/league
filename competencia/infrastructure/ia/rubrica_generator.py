from decimal import Decimal, ROUND_HALF_UP

from ...domain.entities.criterio_ia import CriterioIA
from ...domain.ports.rubrica_generator_port import RubricaGeneratorPort
from ...domain.value_objects.enums.tipo_torneo import TipoTorneo
from ...domain.value_objects.enums.nivel_tecnico import NivelTecnico
from ...domain.value_objects.enums.categoria import Categoria
from ...domain.value_objects.enums.tipo_dato import TipoDato


# ─── Spec de un criterio en las plantillas ────────────────────────────────────
# (nombre, descripcion, tipo_dato, peso, val_min, val_max, mayor_es_mejor)
_CSpec = tuple[str, str, TipoDato, float, float | None, float | None, bool]


def _num(nombre, desc, peso, vmin, vmax, mayor=True) -> _CSpec:
    return (nombre, desc, TipoDato.NUMERICO, peso, vmin, vmax, mayor)


def _bool(nombre, desc, peso, mayor=True) -> _CSpec:
    return (nombre, desc, TipoDato.BOOLEANO, peso, None, None, mayor)


# ─── Plantillas por (TipoTorneo, NivelTecnico) ────────────────────────────────
_TEMPLATES: dict[tuple[TipoTorneo, NivelTecnico], list[_CSpec]] = {

    # ── KNOCKOUT ────────────────────────────────────────────────────────────
    (TipoTorneo.KNOCKOUT, NivelTecnico.BASICO): [
        _bool("Funcionamiento del Robot",   "El robot completó la tarea asignada sin intervención.", 40),
        _num("Tiempo de Ejecución",         "Tiempo total en segundos para completar la tarea.",      30, 0, 300, mayor=False),
        _num("Creatividad del Diseño",      "Originalidad y creatividad observada en la solución.",   20, 0, 10),
        _num("Presentación del Equipo",     "Claridad al presentar su robot y proceso de diseño.",    10, 0, 10),
    ],
    (TipoTorneo.KNOCKOUT, NivelTecnico.INTERMEDIO): [
        _num("Precisión de Navegación",     "Porcentaje de objetivos alcanzados con precisión.",      25, 0, 100),
        _num("Tiempo de Ejecución",         "Tiempo total en segundos para completar la tarea.",      20, 0, 600, mayor=False),
        _num("Innovación Técnica",          "Nivel de innovación en la solución implementada.",       20, 0, 10),
        _num("Trabajo en Equipo",           "Coordinación y colaboración demostrada por el equipo.",  15, 0, 10),
        _num("Diseño de Solución",          "Calidad del diseño mecánico y lógico del robot.",        10, 0, 10),
        _bool("Cumplimiento de Objetivos",  "El robot cumplió todos los objetivos planteados.",       10),
    ],
    (TipoTorneo.KNOCKOUT, NivelTecnico.AVANZADO): [
        _num("Precisión Técnica",           "Exactitud en la ejecución de las tareas asignadas.",     25, 0, 100),
        _num("Eficiencia Algorítmica",      "Optimización del algoritmo de control empleado.",        20, 0, 100),
        _num("Tiempo de Ejecución",         "Tiempo total en segundos para completar la tarea.",      15, 0, 600, mayor=False),
        _num("Innovación y Creatividad",    "Soluciones originales e ingeniosas aplicadas.",          15, 0, 10),
        _num("Documentación Técnica",       "Calidad y completitud de la documentación presentada.",  10, 0, 10),
        _num("Trabajo en Equipo",           "Coordinación efectiva y roles claramente definidos.",    10, 0, 10),
        _bool("Cumplimiento de Objetivos",  "El robot cumplió todos los objetivos planteados.",        5),
    ],

    # ── ROUND_ROBIN ─────────────────────────────────────────────────────────
    (TipoTorneo.ROUND_ROBIN, NivelTecnico.BASICO): [
        _bool("Funcionamiento del Robot",   "El robot completó la tarea asignada sin intervención.", 35),
        _num("Puntuación Acumulada",        "Puntaje total obtenido en todas las rondas.",            30, 0, 100),
        _num("Tiempo Promedio",             "Tiempo promedio en segundos por ronda.",                 20, 0, 300, mayor=False),
        _num("Consistencia",               "Regularidad del desempeño a lo largo de las rondas.",    15, 0, 10),
    ],
    (TipoTorneo.ROUND_ROBIN, NivelTecnico.INTERMEDIO): [
        _num("Puntuación Acumulada",        "Puntaje total obtenido en todas las rondas.",            30, 0, 100),
        _num("Consistencia de Desempeño",   "Regularidad del desempeño en las rondas disputadas.",    20, 0, 10),
        _num("Tiempo Promedio por Ronda",   "Tiempo promedio en segundos por ronda completada.",      20, 0, 600, mayor=False),
        _num("Innovación Técnica",          "Nivel de innovación en la solución implementada.",       15, 0, 10),
        _num("Trabajo en Equipo",           "Coordinación y colaboración demostrada por el equipo.",  15, 0, 10),
    ],
    (TipoTorneo.ROUND_ROBIN, NivelTecnico.AVANZADO): [
        _num("Puntuación Acumulada",        "Puntaje total obtenido en todas las rondas.",            25, 0, 100),
        _num("Eficiencia Algorítmica",      "Optimización del algoritmo de control empleado.",        20, 0, 100),
        _num("Consistencia de Desempeño",   "Regularidad del desempeño en las rondas disputadas.",    20, 0, 10),
        _num("Tiempo Promedio por Ronda",   "Tiempo promedio en segundos por ronda completada.",      15, 0, 600, mayor=False),
        _num("Adaptabilidad",               "Capacidad de ajustar la estrategia entre rondas.",       10, 0, 10),
        _num("Documentación Técnica",       "Calidad y completitud de la documentación presentada.",  10, 0, 10),
    ],

    # ── HYBRID ──────────────────────────────────────────────────────────────
    (TipoTorneo.HYBRID, NivelTecnico.BASICO): [
        _bool("Pase de Fase Grupal",        "El equipo superó la fase de grupos.",                   35),
        _num("Puntuación en Grupos",        "Puntaje total obtenido en la fase grupal.",              30, 0, 100),
        _num("Tiempo de Ejecución Final",   "Tiempo en segundos en la fase eliminatoria.",            20, 0, 300, mayor=False),
        _num("Creatividad",                "Originalidad y creatividad observada en la solución.",    15, 0, 10),
    ],
    (TipoTorneo.HYBRID, NivelTecnico.INTERMEDIO): [
        _num("Puntuación en Grupos",        "Puntaje total acumulado en la fase grupal.",             25, 0, 100),
        _num("Precisión en Eliminatorias",  "Exactitud en las tareas durante la fase eliminatoria.",  25, 0, 100),
        _num("Tiempo de Ejecución",         "Tiempo total en segundos en la fase eliminatoria.",      20, 0, 600, mayor=False),
        _num("Innovación Técnica",          "Nivel de innovación en la solución implementada.",       15, 0, 10),
        _num("Trabajo en Equipo",           "Coordinación y colaboración demostrada por el equipo.",  15, 0, 10),
    ],
    (TipoTorneo.HYBRID, NivelTecnico.AVANZADO): [
        _num("Puntuación en Grupos",        "Puntaje total acumulado en la fase grupal.",             20, 0, 100),
        _num("Precisión en Eliminatorias",  "Exactitud en las tareas durante la fase eliminatoria.",  20, 0, 100),
        _num("Eficiencia Algorítmica",      "Optimización del algoritmo de control empleado.",        20, 0, 100),
        _num("Tiempo de Ejecución",         "Tiempo total en segundos en la fase eliminatoria.",      15, 0, 600, mayor=False),
        _num("Innovación y Creatividad",    "Soluciones originales e ingeniosas aplicadas.",          15, 0, 10),
        _num("Documentación Técnica",       "Calidad y completitud de la documentación presentada.",  10, 0, 10),
    ],
}

# Plantilla de respaldo si no hay coincidencia exacta
_FALLBACK: list[_CSpec] = [
    _num("Rendimiento General",    "Desempeño global del robot durante la competencia.",          35, 0, 100),
    _num("Tiempo de Ejecución",    "Tiempo en segundos para completar las tareas.",               25, 0, 600, mayor=False),
    _num("Innovación Técnica",     "Nivel de innovación en la solución implementada.",            20, 0, 10),
    _num("Trabajo en Equipo",      "Coordinación y colaboración demostrada por el equipo.",       20, 0, 10),
]


class RubricaGenerator(RubricaGeneratorPort):
    """
    Generador de rúbricas basado en plantillas para torneos de robótica.
    Garantiza que la suma de peso_porcentual sea exactamente 100.00%.
    """

    def generar(
        self,
        torneo_id: str,
        sesion_ia_id: str,
        tipo_torneo: TipoTorneo,
        nivel: NivelTecnico,
        categoria: Categoria,
    ) -> list[CriterioIA]:
        specs = _TEMPLATES.get((tipo_torneo, nivel), _FALLBACK)
        specs = self._ajustar_por_categoria(specs, categoria)
        specs = self._normalizar_pesos(specs)

        criterios: list[CriterioIA] = []
        for orden, (nombre, desc, tipo, peso, vmin, vmax, mayor) in enumerate(specs, start=1):
            criterios.append(
                CriterioIA.create(
                    torneo_id=torneo_id,
                    sesion_ia_id=sesion_ia_id,
                    nombre=nombre,
                    descripcion=desc,
                    tipo_dato=tipo,
                    peso_porcentual=peso,
                    mayor_es_mejor=mayor,
                    orden=orden,
                    valor_minimo=vmin,
                    valor_maximo=vmax,
                )
            )
        return criterios

    # ------------------------------------------------------------------ #

    @staticmethod
    def _ajustar_por_categoria(specs: list[_CSpec], categoria: Categoria) -> list[_CSpec]:
        """
        Para PRIMARY, añade un criterio de seguridad sustituyendo el último criterio
        de menor peso si ya existen 10 o más criterios.
        """
        if categoria != Categoria.PRIMARY:
            return specs

        seguridad: _CSpec = _bool(
            "Seguridad y Normas",
            "El equipo siguió todas las normas de seguridad durante la competencia.",
            10,  # normalizar_pesos redistribuirá todos los pesos proporcionalmente
        )
        return list(specs) + [seguridad]

    @staticmethod
    def _normalizar_pesos(specs: list[_CSpec]) -> list[_CSpec]:
        """
        Redistribuye pesos para que sumen exactamente 100.00%.
        Ajusta el último ítem para absorber el residuo de redondeo.
        """
        total_bruto = sum(s[3] for s in specs)
        if total_bruto == 0:
            # Distribución uniforme si los pesos son cero (caso seguridad añadida)
            base = Decimal("100.00") / len(specs)
            ajustados = [base] * len(specs)
        else:
            ajustados = [
                (Decimal(str(s[3])) / Decimal(str(total_bruto)) * Decimal("100")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                for s in specs
            ]

        # Corregir residuo de redondeo en el último ítem
        residuo = Decimal("100.00") - sum(ajustados)
        ajustados[-1] += residuo

        return [
            (s[0], s[1], s[2], float(p), s[4], s[5], s[6])
            for s, p in zip(specs, ajustados)
        ]
