from django.urls import path
from .views import (
    predecir_resultado, historial_simulacion,
    obtener_retos, analizar_programacion, analizar_componentes, listar_analisis,
)

urlpatterns = [
    path('predecir/', predecir_resultado, name='sim-predecir'),
    path('historial/<int:participante_id>/', historial_simulacion, name='sim-historial'),
    path('retos/<str:torneo_id>/', obtener_retos, name='sim-retos-obtener'),
    path('analisis/programacion/', analizar_programacion, name='sim-analisis-programacion'),
    path('analisis/componentes/', analizar_componentes, name='sim-analisis-componentes'),
    path('analisis/<str:participante_id>/<str:torneo_id>/', listar_analisis, name='sim-analisis-listar'),
]
