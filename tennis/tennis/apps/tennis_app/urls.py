from django.urls import path
from . import views

app_name = 'tennis_app'

urlpatterns = [
    path('', views.main, name='main'),
    path('demo_play', views.demo_play, name='demo_play'),
    path('my_tournaments', views.my_tournaments, name='my_tournaments'),
    path('rules', views.rules, name='rules'),
    path('auth/', views.login_register_view, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    path('club/', views.my_club, name='my_club'),
    path('club/<int:club_id>/', views.club_detail, name='club_detail'),
    path('club/create/', views.create_club, name='create_club'),
    path('club/<int:club_id>/add_tournament/', views.add_tournament, name='add_tournament'),
    path('club/<int:club_id>/add_event/', views.add_event, name='add_event'),
    path('club/<int:club_id>/add_player/', views.add_player, name='add_player'), 
    path('friend_play', views.friend_play, name='friend_play'),
    path('api/save_friendly_game/', views.save_friendly_game, name='save_friendly_game'),
    ]