from simulacion.infrastructure.ia.scoring_engine import ejecutar_scoring, calcular_scores

CRITERIOS_TEST = [
    {
        'criterio_id':            'c1',
        'criterio_nombre':        'Test',
        'criterio_descripcion':   'desc',
        'peso':                   100.0,
        'min_value_qualification': 0.0,
        'max_value_qualification': 10.0,
    }
]
ENTREGABLE_TEST = 'x' * 200


def test_scoring_determinista():
    r1 = ejecutar_scoring(ENTREGABLE_TEST, CRITERIOS_TEST)
    r2 = ejecutar_scoring(ENTREGABLE_TEST, CRITERIOS_TEST)
    assert r1 == r2, 'El motor de scoring no es determinista'
