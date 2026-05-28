from simulacion.application.use_cases.ejecutar_simulacion import generar_retroalimentacion


def test_retroalimentacion_determinista():
    kwargs = dict(
        puntaje_total=72.5,
        posicion=3,
        total_equipos=8,
        fortalezas=[],
        debilidades=[{'nombre': 'X', 'motivo': 'Y', 'valor_normalizado': 40.0}],
    )
    r1 = generar_retroalimentacion(**kwargs)
    r2 = generar_retroalimentacion(**kwargs)
    assert r1 == r2
