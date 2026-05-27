from django.db import models
from django.utils import timezone


class SimulacionPredictiva(models.Model):
    participante_id       = models.IntegerField(db_index=True)
    torneo_id             = models.IntegerField(db_index=True)

    tiempo_estimado       = models.FloatField()
    complejidad_codigo    = models.IntegerField()
    colisiones_historicas = models.IntegerField()
    telemetria_json       = models.JSONField(default=dict)

    puntaje_estimado      = models.FloatField(null=True, blank=True)
    tiempo_probable_fin   = models.FloatField(null=True, blank=True)
    rmse_validacion       = models.FloatField(null=True, blank=True)

    creado_en             = models.DateTimeField(default=timezone.now)
    modelo_version        = models.CharField(max_length=20, default='v1')
    es_oficial            = models.BooleanField(default=False)

    class Meta:
        db_table = 'simulacion_predictiva'
        indexes = [
            models.Index(fields=['participante_id', 'torneo_id']),
            models.Index(fields=['creado_en']),
        ]
