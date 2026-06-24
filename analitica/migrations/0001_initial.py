import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SugerenciaDecisionModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('torneo_id', models.CharField(db_index=True, max_length=36)),
                ('tipo', models.CharField(
                    choices=[
                        ('REPROGRAMACION',  'Reprogramación'),
                        ('AJUSTE_CRITERIO', 'Ajuste de Criterio'),
                        ('APOYO_EQUIPO',    'Apoyo a Equipo'),
                        ('OTRO',            'Otro'),
                    ],
                    max_length=20,
                )),
                ('descripcion', models.TextField()),
                ('accion_sugerida', models.TextField(blank=True, default='')),
                ('entidad_ref_id', models.CharField(blank=True, default='', max_length=36)),
                ('severidad', models.CharField(
                    choices=[('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error')],
                    default='INFO',
                    max_length=10,
                )),
                ('estado', models.CharField(
                    choices=[
                        ('PENDIENTE',  'Pendiente'),
                        ('ATENDIDA',   'Atendida'),
                        ('DESCARTADA', 'Descartada'),
                    ],
                    default='PENDIENTE',
                    max_length=15,
                )),
                ('generado_en', models.DateTimeField(auto_now_add=True)),
                ('atendida_en', models.DateTimeField(blank=True, null=True)),
            ],
            options={'db_table': 'analitica_sugerencia_decision'},
        ),
        migrations.AlterUniqueTogether(
            name='sugerenciadecisionmodel',
            unique_together={('torneo_id', 'tipo', 'entidad_ref_id')},
        ),
        migrations.AddIndex(
            model_name='sugerenciadecisionmodel',
            index=models.Index(
                fields=['torneo_id', 'estado'],
                name='an_sug_torneo_estado_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='sugerenciadecisionmodel',
            index=models.Index(
                fields=['torneo_id', 'tipo', 'entidad_ref_id'],
                name='an_sug_torneo_tipo_ref_idx',
            ),
        ),
    ]
