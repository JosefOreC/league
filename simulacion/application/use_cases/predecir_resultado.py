from simulacion.infrastructure.ml.xgboost_adapter import XGBoostAdapter
from simulacion.infrastructure.adapters.output.models import SimulacionPredictiva


class PredecirResultadoUseCase:

    def ejecutar(self, data: dict) -> SimulacionPredictiva:
        features = {
            'tiempo_estimado': data['tiempo_estimado'],
            'complejidad_codigo': data['complejidad_codigo'],
            'colisiones_historicas': data['colisiones_historicas'],
            'telemetria_velocidad_prom': data['telemetria_velocidad_prom'],
            'telemetria_errores': data['telemetria_errores'],
        }

        adapter = XGBoostAdapter()
        prediccion = adapter.predecir(features)

        sim = SimulacionPredictiva.objects.create(
            participante_id=data['participante_id'],
            torneo_id=data['torneo_id'],
            tiempo_estimado=data['tiempo_estimado'],
            complejidad_codigo=data['complejidad_codigo'],
            colisiones_historicas=data['colisiones_historicas'],
            telemetria_json={
                'velocidad_prom': data['telemetria_velocidad_prom'],
                'errores': data['telemetria_errores'],
            },
            puntaje_estimado=prediccion['puntaje_estimado'],
            tiempo_probable_fin=prediccion['tiempo_probable_fin'],
        )

        return sim
