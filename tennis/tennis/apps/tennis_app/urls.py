from django.urls import path
from . import views

app_name = 'tennis_app'

urlpatterns = [
    path('', views.main, name='main')
]