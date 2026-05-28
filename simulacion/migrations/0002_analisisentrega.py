import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalisisEntrega',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reto_id', models.CharField(db_index=True, max_length=36)),
                ('participante_id', models.CharField(db_index=True, max_length=36)),
                ('torneo_id', models.CharField(db_index=True, max_length=36)),
                ('caso', models.CharField(choices=[('PROGRAMACION', 'Programación'), ('COMPONENTES', 'Componentes')], max_length=20)),
                ('contenido_entrega', models.TextField()),
                ('calificaciones_por_criterio', models.JSONField(default=list)),
                ('puntaje_total_simulado', models.FloatField()),
                ('observacion_general', models.TextField(blank=True, default='')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'simulacion_analisis_entrega',
            },
        ),
        migrations.AddIndex(
            model_name='analisisentrega',
            index=models.Index(fields=['participante_id', 'torneo_id'], name='sim_analisis_part_torn_idx'),
        ),
        migrations.AddIndex(
            model_name='analisisentrega',
            index=models.Index(fields=['reto_id'], name='sim_analisis_reto_idx'),
        ),
    ]
