import uuid as _uuid
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


class AnalisisEntrega(models.Model):
    CASO_CHOICES = [
        ('PROGRAMACION', 'Programación'),
        ('COMPONENTES',  'Componentes'),
    ]

    id                          = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    reto_id                     = models.CharField(max_length=36, db_index=True)
    participante_id             = models.CharField(max_length=36, db_index=True)
    torneo_id                   = models.CharField(max_length=36, db_index=True)
    caso                        = models.CharField(max_length=20, choices=CASO_CHOICES)
    contenido_entrega           = models.TextField()
    calificaciones_por_criterio = models.JSONField(default=list)
    puntaje_total_simulado      = models.FloatField()
    observacion_general         = models.TextField(blank=True, default='')
    creado_en                   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'simulacion_analisis_entrega'
        indexes  = [
            models.Index(fields=['participante_id', 'torneo_id']),
            models.Index(fields=['reto_id']),
        ]


class SimulacionResultado(models.Model):
    id                    = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    tournament_id         = models.CharField(max_length=36, db_index=True)
    equipo_id             = models.CharField(max_length=36, db_index=True)
    entregable            = models.TextField()

    scores                = models.JSONField(default=list)
    puntaje_total         = models.DecimalField(max_digits=5, decimal_places=2)

    posicion_estimada     = models.IntegerField()
    total_equipos         = models.IntegerField()
    percentil             = models.FloatField()
    advertencia_muestra   = models.CharField(max_length=100, blank=True, default='')

    fortalezas            = models.JSONField(default=list)
    debilidades           = models.JSONField(default=list)

    retro_resumen         = models.TextField(blank=True, default='')
    retro_recomendaciones = models.JSONField(default=list)
    sin_mejoras_criticas  = models.BooleanField(default=False)

    creado_en             = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'simulacion_resultado'
        indexes  = [
            models.Index(fields=['tournament_id', 'equipo_id']),
            models.Index(fields=['creado_en']),
        ]
