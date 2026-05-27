from django.contrib import admin
from simulacion.infrastructure.adapters.output.models import SimulacionPredictiva


@admin.register(SimulacionPredictiva)
class SimulacionPredictivaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'participante_id', 'torneo_id', 'puntaje_estimado',
                     'tiempo_probable_fin', 'modelo_version', 'creado_en']
    list_filter   = ['modelo_version', 'es_oficial']
    search_fields = ['participante_id', 'torneo_id']
    readonly_fields = ['creado_en']
