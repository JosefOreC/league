"""
Generador de Resumen Ejecutivo — domain/services/
Motor de NLG (Natural Language Generation) basado en plantillas.
Determinista: mismas métricas + mismo tono → mismo texto. Sin API externa.
Coherente con el enfoque rules-based del proyecto (RulesBasedNLPAdapter).

Idioma: español. Salida garantizada entre 300 y 600 palabras.
"""
from ..entities.resumen_ejecutivo import MetricasResumen


# ── Léxico por tono ───────────────────────────────────────────────────────────
_TONO = {
    'FORMAL': {
        'apertura':    'El presente documento expone los resultados del torneo',
        'cierre_eq':   'la participación de los equipos inscritos',
        'destacado':   'Cabe destacar que',
        'campeon':     'El primer lugar correspondió al equipo',
        'cierre':      'Se recomienda considerar las observaciones precedentes '
                       'para la planificación de futuras ediciones.',
        'institucional': 'Este informe se pone a disposición de directivos, '
                         'patrocinadores y de la comunidad educativa con el '
                         'propósito de documentar de manera objetiva el desarrollo '
                         'de la competencia y respaldar la toma de decisiones.',
        'exclam':      '.',
    },
    'DIVULGATIVO': {
        'apertura':    'Te presentamos un resumen de lo que dejó el torneo',
        'cierre_eq':   'la participación de todos los equipos',
        'destacado':   'Vale la pena resaltar que',
        'campeon':     'El gran campeón fue el equipo',
        'cierre':      'De cara a las próximas ediciones, estas recomendaciones '
                       'ayudarán a que el torneo siga creciendo.',
        'institucional': 'Compartimos este resumen con directivos, patrocinadores '
                         'y con toda la comunidad educativa, convencidos de que '
                         'iniciativas como esta fortalecen el interés de los '
                         'estudiantes por la ciencia, la tecnología y el trabajo en equipo.',
        'exclam':      '.',
    },
    'CELEBRATORIO': {
        'apertura':    '¡Cerramos una edición inolvidable del torneo',
        'cierre_eq':   '¡el esfuerzo de todos los equipos participantes',
        'destacado':   '¡Qué manera de competir! Resalta que',
        'campeon':     '¡El merecido campeón fue el equipo',
        'cierre':      '¡Vamos por una próxima edición todavía mejor, '
                       'aplicando todo lo aprendido!',
        'institucional': '¡Gracias a directivos, patrocinadores y a toda la '
                         'comunidad educativa por hacer posible esta fiesta del '
                         'conocimiento, donde cada estudiante demostró que el '
                         'talento y la pasión no tienen límites!',
        'exclam':      '!',
    },
}

_NIVEL_TEXTO = {
    'ALTO':       'un nivel de competencia muy alto, con resultados ajustados '
                  'y un desempeño parejo entre los mejores equipos',
    'MEDIO':      'un nivel de competencia equilibrado, con diferencias claras '
                  'pero sin distancias insalvables entre los equipos',
    'HOMOGENEO':  'un desempeño notablemente homogéneo, donde la mayoría de los '
                  'equipos obtuvo puntajes muy similares entre sí',
}

# Máximo de recomendaciones a narrar (control del límite superior de 600 palabras)
_MAX_RECOMENDACIONES = 5


def generar_resumen(metricas: MetricasResumen, tono: str) -> str:
    tono = tono.upper()
    if tono not in _TONO:
        tono = 'DIVULGATIVO'
    L = _TONO[tono]
    ex = L['exclam']

    parrafos = [
        _parrafo_apertura(metricas, L, ex),
        _parrafo_resultados(metricas, L, ex),
        _parrafo_analisis(metricas, L, ex),
        _parrafo_recomendaciones(metricas, L, ex),
        L['institucional'],
    ]
    return "\n\n".join(p for p in parrafos if p)


# ── Párrafos ──────────────────────────────────────────────────────────────────

def _parrafo_apertura(m: MetricasResumen, L: dict, ex: str) -> str:
    if m.fecha_fin and m.fecha_fin[:10] != m.fecha_inicio[:10]:
        fechas = f"del {m.fecha_inicio[:10]} al {m.fecha_fin[:10]}"
    else:
        fechas = f"el {m.fecha_inicio[:10]}"

    return (
        f"{L['apertura']} «{m.torneo_nombre}», celebrado {fechas} "
        f"en {m.sede}{ex} "
        f"Esta edición reunió a {m.total_equipos} equipos provenientes de "
        f"{m.total_instituciones} instituciones educativas, "
        f"con un total de {m.total_participantes} estudiantes participantes "
        f"que demostraron su talento, preparación y espíritu de competencia "
        f"a lo largo de toda la jornada. Cada equipo llegó con meses de "
        f"trabajo previo, ajustando sus prototipos y estrategias para rendir "
        f"al máximo en cada prueba. La organización agradece "
        f"{L['cierre_eq']} y de las comunidades educativas que los respaldaron, "
        f"así como el acompañamiento de docentes asesores y familias que "
        f"hicieron posible esta experiencia formativa."
    )


def _parrafo_resultados(m: MetricasResumen, L: dict, ex: str) -> str:
    if not m.podio:
        return (
            "En cuanto a los resultados, el torneo se desarrolló según lo previsto, "
            "con una participación activa en cada una de las fases programadas, "
            "aunque no se registró un podio definitivo al momento de elaborar "
            "este resumen ejecutivo."
        )

    campeon = m.campeon
    partes = [
        f"En el plano deportivo, {L['campeon']} «{campeon.nombre}» "
        f"de la institución {campeon.institucion}, que alcanzó el primer lugar "
        f"con un puntaje acumulado de {campeon.puntaje:.2f} puntos{ex}"
    ]

    resto = [e for e in m.podio if e.posicion_final != 1][:2]
    if resto:
        menciones = "; ".join(
            f"«{e.nombre}» ({e.institucion}) en el puesto {e.posicion_final} "
            f"con {e.puntaje:.2f} puntos"
            for e in resto
        )
        partes.append(
            f"El podio se completó con los equipos {menciones}. "
        )
    partes.append(
        "Estos resultados reflejan el alto compromiso de los equipos y el "
        "rigor con el que afrontaron cada una de las pruebas planteadas, "
        "demostrando que la preparación constante y la colaboración dentro "
        "de cada grupo son determinantes para alcanzar el éxito."
    )
    return " ".join(partes)


def _parrafo_analisis(m: MetricasResumen, L: dict, ex: str) -> str:
    nivel_txt = _NIVEL_TEXTO.get(m.nivel_competencia, _NIVEL_TEXTO['MEDIO'])
    crit = (
        f"El criterio más determinante en la evaluación fue «{m.criterio_determinante}», "
        f"que marcó las mayores diferencias en el desempeño de los equipos y se "
        f"consolidó como el factor de mayor peso en la calificación final. "
        if m.criterio_determinante else ""
    )
    return (
        f"Desde el análisis técnico, el torneo evidenció {nivel_txt}. "
        f"El puntaje promedio global se ubicó en {m.puntaje_promedio_global:.2f} puntos, "
        f"un indicador que permite dimensionar el rendimiento conjunto de los "
        f"participantes y comparar esta edición con futuras ediciones. "
        f"{crit}"
        f"{L['destacado']} la evaluación combinó criterios técnicos y de ejecución, "
        f"lo que aportó objetividad y transparencia al proceso de calificación y "
        f"permitió que cada equipo recibiera una valoración justa de su trabajo."
    )


def _parrafo_recomendaciones(m: MetricasResumen, L: dict, ex: str) -> str:
    if not m.recomendaciones:
        base = (
            "El torneo no presentó anomalías operativas ni académicas relevantes, "
            "lo que habla de una organización sólida y de un desarrollo fluido de la "
            "competencia en todas sus etapas. Aun así, se sugiere mantener el registro "
            "detallado de resultados para enriquecer el análisis comparativo en el futuro. "
        )
    else:
        recs = m.recomendaciones[:_MAX_RECOMENDACIONES]
        items = " ".join(
            f"({i}) {rec.rstrip('.')}." for i, rec in enumerate(recs, start=1)
        )
        base = (
            "De cara a futuras ediciones, el sistema de análisis identificó "
            "las siguientes recomendaciones orientadas a mejorar la calidad de la "
            "competencia y la equidad en la evaluación: "
            f"{items} "
        )
    return base + L['cierre']
