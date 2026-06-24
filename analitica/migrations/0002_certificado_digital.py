import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analitica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificadoDigitalModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False,
                                        primary_key=True, serialize=False)),
                ('torneo_id', models.CharField(db_index=True, max_length=36)),
                ('participante_id', models.CharField(blank=True, max_length=36, null=True)),
                ('equipo_id', models.CharField(blank=True, max_length=36, null=True)),
                ('tipo_certificado', models.CharField(
                    choices=[
                        ('PARTICIPACION',    'Participación'),
                        ('GANADOR',          'Ganador'),
                        ('MENCION_ESPECIAL', 'Mención Especial'),
                    ],
                    max_length=20,
                )),
                ('nombres_destinatario', models.CharField(max_length=300)),
                ('institucion', models.CharField(max_length=300)),
                ('posicion_final', models.IntegerField(blank=True, null=True)),
                ('medalla', models.CharField(
                    blank=True,
                    choices=[('ORO', 'Oro'), ('PLATA', 'Plata'), ('BRONCE', 'Bronce')],
                    max_length=10,
                    null=True,
                )),
                ('url_pdf', models.CharField(blank=True, default='', max_length=500)),
                ('codigo_verificacion', models.CharField(max_length=64, unique=True)),
                ('generado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'analitica_certificado_digital'},
        ),
        migrations.AddIndex(
            model_name='certificadodigitalmodel',
            index=models.Index(
                fields=['torneo_id', 'tipo_certificado'],
                name='an_cert_torneo_tipo_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='certificadodigitalmodel',
            index=models.Index(
                fields=['participante_id'],
                name='an_cert_participante_idx',
            ),
        ),
    ]
