from django.urls import path
from .views import predecir_resultado, historial_simulacion

urlpatterns = [
    path('predecir/', predecir_resultado, name='sim-predecir'),
    path('historial/<int:participante_id>/', historial_simulacion, name='sim-historial'),
]
