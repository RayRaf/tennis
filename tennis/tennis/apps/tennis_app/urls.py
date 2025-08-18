from django.urls import path
from . import views

app_name = 'tennis_app'

urlpatterns = [
    path('', views.main, name='main'),
    path('demo_play', views.demo_play, name='demo_play'),
    path('my_tournaments', views.my_tournaments, name='my_tournaments'),
    path('rules', views.rules, name='rules'),
    path('settings', views.settings_view, name='settings'),
    path('auth/', views.login_register_view, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    path('club/', views.my_club, name='my_club'),
    path('club/<int:club_id>/', views.club_detail, name='club_detail'),
    path('club/create/', views.create_club, name='create_club'),
    path('club/<int:club_id>/add_tournament/', views.add_tournament, name='add_tournament'),
    path('club/<int:club_id>/add_event/', views.add_event, name='add_event'),
    path('club/<int:club_id>/add_player/', views.add_player, name='add_player'), 
    path('tournament/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    path('tournament/<int:tournament_id>/add_participant/', views.add_participant, name='add_participant'),
    path('tournament/<int:tournament_id>/generate_matches/', views.generate_matches, name='generate_matches'),
    path('match/<int:match_id>/report/', views.report_match_result, name='report_match_result'),
    path('match/<int:match_id>/play/', views.play_match_live, name='play_match_live'),
    path('club/<int:club_id>/invite_admin/', views.invite_admin, name='invite_admin'),
    path('invite/accept/', views.accept_invite, name='accept_invite'),
    path('friend_play', views.friend_play, name='friend_play'),
    path('api/save_friendly_game/', views.save_friendly_game, name='save_friendly_game'),
    # Removed direct references to old templates for clarity
    # path('old_template_path/', views.old_template_view, name='old_template'),
    # path('another_old_template/', views.another_old_template_view, name='another_old_template'),
    ]