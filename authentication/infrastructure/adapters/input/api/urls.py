from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login),
    path('register/', register),
    path('me/', me),
    path('logout/', logout),
    path('refresh/', refresh),
]