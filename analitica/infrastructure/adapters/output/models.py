import uuid as _uuid

from django.db import models


class CertificadoDigitalModel(models.Model):
    TIPO_CHOICES = [
        ('PARTICIPACION',    'Participación'),
        ('GANADOR',          'Ganador'),
        ('MENCION_ESPECIAL', 'Mención Especial'),
    ]
    MEDALLA_CHOICES = [
        ('ORO',    'Oro'),
        ('PLATA',  'Plata'),
        ('BRONCE', 'Bronce'),
    ]

    id                   = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    torneo_id            = models.CharField(max_length=36, db_index=True)
    participante_id      = models.CharField(max_length=36, null=True, blank=True)
    equipo_id            = models.CharField(max_length=36, null=True, blank=True)
    tipo_certificado     = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nombres_destinatario = models.CharField(max_length=300)
    institucion          = models.CharField(max_length=300)
    posicion_final       = models.IntegerField(null=True, blank=True)
    medalla              = models.CharField(max_length=10, choices=MEDALLA_CHOICES,
                                            null=True, blank=True)
    url_pdf              = models.CharField(max_length=500, blank=True, default='')
    codigo_verificacion  = models.CharField(max_length=64, unique=True)
    generado_en          = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analitica_certificado_digital'
        indexes  = [
            models.Index(fields=['torneo_id', 'tipo_certificado'],
                         name='an_cert_torneo_tipo_idx'),
            models.Index(fields=['participante_id'],
                         name='an_cert_participante_idx'),
        ]


class ResumenEjecutivoModel(models.Model):
    TONO_CHOICES = [
        ('FORMAL',       'Formal'),
        ('DIVULGATIVO',  'Divulgativo'),
        ('CELEBRATORIO', 'Celebratorio'),
    ]

    id              = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    torneo_id       = models.CharField(max_length=36, db_index=True)
    resumen_texto   = models.TextField()
    tono            = models.CharField(max_length=15, choices=TONO_CHOICES, default='DIVULGATIVO')
    version         = models.IntegerField(default=1)
    metricas_usadas = models.JSONField(default=dict)
    url_pdf         = models.CharField(max_length=500, blank=True, default='')
    generado_en     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analitica_resumen_ejecutivo'
        indexes  = [
            models.Index(fields=['torneo_id', 'version'],
                         name='an_resumen_torneo_ver_idx'),
        ]


class SugerenciaDecisionModel(models.Model):
    TIPO_CHOICES = [
        ('REPROGRAMACION',  'Reprogramación'),
        ('AJUSTE_CRITERIO', 'Ajuste de Criterio'),
        ('APOYO_EQUIPO',    'Apoyo a Equipo'),
        ('OTRO',            'Otro'),
    ]
    SEVERIDAD_CHOICES = [
        ('INFO',    'Info'),
        ('WARNING', 'Warning'),
        ('ERROR',   'Error'),
    ]
    ESTADO_CHOICES = [
        ('PENDIENTE',   'Pendiente'),
        ('ATENDIDA',    'Atendida'),
        ('DESCARTADA',  'Descartada'),
    ]

    id             = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    torneo_id      = models.CharField(max_length=36, db_index=True)
    tipo           = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion    = models.TextField()
    accion_sugerida = models.TextField(blank=True, default='')
    entidad_ref_id = models.CharField(max_length=36, blank=True, default='')
    severidad      = models.CharField(max_length=10, choices=SEVERIDAD_CHOICES, default='INFO')
    estado         = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')
    generado_en    = models.DateTimeField(auto_now_add=True)
    atendida_en    = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'analitica_sugerencia_decision'
        unique_together = [('torneo_id', 'tipo', 'entidad_ref_id')]
        indexes = [
            models.Index(fields=['torneo_id', 'estado'],
                         name='an_sug_torneo_estado_idx'),
            models.Index(fields=['torneo_id', 'tipo', 'entidad_ref_id'],
                         name='an_sug_torneo_tipo_ref_idx'),
        ]
