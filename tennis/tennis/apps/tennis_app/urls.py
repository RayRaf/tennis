from django.urls import path
from . import views

app_name = 'tennis_app'

urlpatterns = [
    path('', views.main, name='main'),
    path('free_play', views.play, name='free_play'),
    path('my_tournaments', views.my_tournaments, name='my_tournaments'),
    path('rules', views.rules, name='rules'),
    ]