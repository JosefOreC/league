from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SimulacionPredictiva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participante_id', models.IntegerField(db_index=True)),
                ('torneo_id', models.IntegerField(db_index=True)),
                ('tiempo_estimado', models.FloatField()),
                ('complejidad_codigo', models.IntegerField()),
                ('colisiones_historicas', models.IntegerField()),
                ('telemetria_json', models.JSONField(default=dict)),
                ('puntaje_estimado', models.FloatField(blank=True, null=True)),
                ('tiempo_probable_fin', models.FloatField(blank=True, null=True)),
                ('rmse_validacion', models.FloatField(blank=True, null=True)),
                ('creado_en', models.DateTimeField(default=django.utils.timezone.now)),
                ('modelo_version', models.CharField(default='v1', max_length=20)),
                ('es_oficial', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'simulacion_predictiva',
            },
        ),
        migrations.AddIndex(
            model_name='simulacionpredictiva',
            index=models.Index(fields=['participante_id', 'torneo_id'], name='simulacion__partici_torneo_idx'),
        ),
        migrations.AddIndex(
            model_name='simulacionpredictiva',
            index=models.Index(fields=['creado_en'], name='simulacion__creado__idx'),
        ),
    ]
