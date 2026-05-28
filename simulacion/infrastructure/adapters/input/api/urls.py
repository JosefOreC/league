from django.urls import path
from .views import test

urlpatterns = [
    path('', test),
    
    # Apuntamos temporalmente a 'test' para que el endpoint responda con éxito
    path('torneo/<uuid:tournament_id>/simular/', test, name='simular-simulacion'),
]
