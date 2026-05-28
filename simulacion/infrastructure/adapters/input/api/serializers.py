from rest_framework import serializers
from simulacion.infrastructure.adapters.output.models import SimulacionPredictiva, AnalisisEntrega


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


class AnalizarProgramacionInputSerializer(serializers.Serializer):
    reto_id         = serializers.CharField()
    participante_id = serializers.CharField()
    torneo_id       = serializers.CharField()
    codigo_fuente   = serializers.CharField()


class AnalizarComponentesInputSerializer(serializers.Serializer):
    reto_id              = serializers.CharField()
    participante_id      = serializers.CharField()
    torneo_id            = serializers.CharField()
    descripcion_solucion = serializers.CharField()


class AnalisisEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AnalisisEntrega
        fields = ['id', 'caso', 'reto_id', 'puntaje_total_simulado',
                  'calificaciones_por_criterio', 'observacion_general', 'creado_en']
