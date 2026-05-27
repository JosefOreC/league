import joblib
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent / 'xgboost_model.pkl'


class XGBoostAdapter:
    def __init__(self):
        self._model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

    def predecir(self, features: dict) -> dict:
        if self._model is None:
            raise RuntimeError('Modelo no entrenado. Ejecutar train_model primero.')
        X = np.array([[
            features['tiempo_estimado'],
            features['complejidad_codigo'],
            features['colisiones_historicas'],
            features['telemetria_velocidad_prom'],
            features['telemetria_errores'],
        ]])
        puntaje = float(self._model.predict(X)[0])
        puntaje = max(0.0, min(100.0, puntaje))
        return {
            'puntaje_estimado': round(puntaje, 2),
            'tiempo_probable_fin': round(features['tiempo_estimado'] * 1.05, 2),
        }
