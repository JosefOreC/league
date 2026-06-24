import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analitica', '0002_certificado_digital'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResumenEjecutivoModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False,
                                        primary_key=True, serialize=False)),
                ('torneo_id', models.CharField(db_index=True, max_length=36)),
                ('resumen_texto', models.TextField()),
                ('tono', models.CharField(
                    choices=[
                        ('FORMAL',       'Formal'),
                        ('DIVULGATIVO',  'Divulgativo'),
                        ('CELEBRATORIO', 'Celebratorio'),
                    ],
                    default='DIVULGATIVO',
                    max_length=15,
                )),
                ('version', models.IntegerField(default=1)),
                ('metricas_usadas', models.JSONField(default=dict)),
                ('url_pdf', models.CharField(blank=True, default='', max_length=500)),
                ('generado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'analitica_resumen_ejecutivo'},
        ),
        migrations.AddIndex(
            model_name='resumenejecutivomodel',
            index=models.Index(
                fields=['torneo_id', 'version'],
                name='an_resumen_torneo_ver_idx',
            ),
        ),
    ]
