from rest_framework import serializers
from simulacion.infrastructure.adapters.output.models import SimulacionPredictiva


class PredecirInputSerializer(serializers.Serializer):
    participante_id           = serializers.IntegerField()
    torneo_id                 = serializers.IntegerField()
    tiempo_estimado           = serializers.FloatField(min_value=0)
    complejidad_codigo        = serializers.IntegerField(min_value=1, max_value=10)
    colisiones_historicas     = serializers.IntegerField(min_value=0)
    telemetria_velocidad_prom = serializers.FloatField(min_value=0)
    telemetria_errores        = serializers.IntegerField(min_value=0)


class PredecirOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulacionPredictiva
        fields = ['id', 'puntaje_estimado', 'tiempo_probable_fin',
                  'rmse_validacion', 'modelo_version']
