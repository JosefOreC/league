import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulacion', '0002_analisisentrega'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimulacionResultado',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tournament_id', models.CharField(db_index=True, max_length=36)),
                ('equipo_id', models.CharField(db_index=True, max_length=36)),
                ('entregable', models.TextField()),
                ('scores', models.JSONField(default=list)),
                ('puntaje_total', models.DecimalField(decimal_places=2, max_digits=5)),
                ('posicion_estimada', models.IntegerField()),
                ('total_equipos', models.IntegerField()),
                ('percentil', models.FloatField()),
                ('advertencia_muestra', models.CharField(blank=True, default='', max_length=100)),
                ('fortalezas', models.JSONField(default=list)),
                ('debilidades', models.JSONField(default=list)),
                ('retro_resumen', models.TextField(blank=True, default='')),
                ('retro_recomendaciones', models.JSONField(default=list)),
                ('sin_mejoras_criticas', models.BooleanField(default=False)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'simulacion_resultado',
            },
        ),
        migrations.AddIndex(
            model_name='simulacionresultado',
            index=models.Index(fields=['tournament_id', 'equipo_id'], name='sim_result_tourn_equipo_idx'),
        ),
        migrations.AddIndex(
            model_name='simulacionresultado',
            index=models.Index(fields=['creado_en'], name='sim_result_creado_idx'),
        ),
    ]
