from django.urls import path
from .views import create_tournament

urlpatterns = [
    path('create/', create_tournament),
]
