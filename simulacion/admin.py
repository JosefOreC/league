from django.contrib import admin
from simulacion.infrastructure.adapters.output.models import (
    SimulacionPredictiva, AnalisisEntrega, SimulacionResultado,
)


@admin.register(SimulacionPredictiva)
class SimulacionPredictivaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'participante_id', 'torneo_id', 'puntaje_estimado',
                     'tiempo_probable_fin', 'modelo_version', 'creado_en']
    list_filter   = ['modelo_version', 'es_oficial']
    search_fields = ['participante_id', 'torneo_id']
    readonly_fields = ['creado_en']


@admin.register(AnalisisEntrega)
class AnalisisEntregaAdmin(admin.ModelAdmin):
    list_display    = ['id', 'caso', 'participante_id', 'torneo_id',
                       'puntaje_total_simulado', 'creado_en']
    list_filter     = ['caso']
    search_fields   = ['participante_id', 'torneo_id', 'reto_id']
    readonly_fields = ['id', 'creado_en']


@admin.register(SimulacionResultado)
class SimulacionResultadoAdmin(admin.ModelAdmin):
    list_display    = ['id', 'tournament_id', 'equipo_id', 'puntaje_total',
                       'posicion_estimada', 'percentil', 'creado_en']
    list_filter     = ['sin_mejoras_criticas']
    search_fields   = ['tournament_id', 'equipo_id']
    readonly_fields = ['id', 'creado_en']
