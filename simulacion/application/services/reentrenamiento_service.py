from django.db import connection

from simulacion.infrastructure.ml.train_model import entrenar
import numpy as np


def obtener_datos_con_resultado_real():
    """JOIN con la tabla real de resultados de competencia."""
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                sp.tiempo_estimado,
                sp.complejidad_codigo,
                sp.colisiones_historicas,
                sp.telemetria_json,
                fr.puntaje_total_acumulado AS puntaje_real
            FROM simulacion_predictiva sp
            INNER JOIN competencia_final_ranking fr
                ON fr.tournament_id::text = sp.torneo_id::text
            WHERE fr.puntaje_total_acumulado IS NOT NULL
        ''')
        return cursor.fetchall()


def reentrenar():
    filas = obtener_datos_con_resultado_real()
    if len(filas) < 10:
        raise ValueError('Datos insuficientes para reentrenar (mínimo 10 registros con resultado real).')

    X, y = [], []
    for fila in filas:
        tiempo_est, complejidad, colisiones, telemetria, puntaje_real = fila
        velocidad_prom = telemetria.get('velocidad_prom', 0.0) if isinstance(telemetria, dict) else 0.0
        errores = telemetria.get('errores', 0) if isinstance(telemetria, dict) else 0
        X.append([tiempo_est, complejidad, colisiones, velocidad_prom, errores])
        y.append(float(puntaje_real))

    return entrenar(np.array(X), np.array(y))
