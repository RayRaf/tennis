from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import LoginForm, RegisterForm

# Create your views here.
def main(request):
    return render(request, 'home_index.html')

def demo_play(request):
    return render(request, 'demo_play.html')


def friend_play(request):
    club_id = request.GET.get("club_id")
    players = []
    if club_id:
        try:
            club = Club.objects.get(id=club_id)
            players = Player.objects.filter(club=club).order_by("full_name")
        except Club.DoesNotExist:
            pass
    return render(request, 'friend_play.html', {"players": players})


def my_tournaments(request):
    return render(request, 'my_tournaments.html')

def rules(request):
    return render(request, 'rules.html')






# .......................................
# Авторизация и регистрация



def login_register_view(request):
    if request.method == 'POST':
        if 'username' in request.POST and 'password1' in request.POST:
            # Это регистрация
            register_form = RegisterForm(request.POST)
            login_form = LoginForm()
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('tennis_app:main')  
            else:
                messages.error(request, 'Ошибка при регистрации.')
        else:
            # Это вход
            login_form = LoginForm(request, data=request.POST)
            register_form = RegisterForm()
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('tennis_app:main')  
            else:
                messages.error(request, 'Неверные данные для входа.')
    else:
        login_form = LoginForm()
        register_form = RegisterForm()

    return render(request, 'login_register.html', {
        'login_form': login_form,
        'register_form': register_form,
    })





def logout_view(request):
    logout(request)
    return redirect('tennis_app:login_register')  # или другая нужная страница


# .......................................
# Основная логика приложения

from django.shortcuts import render, get_object_or_404
from .models import Club, ClubEvent, Tournament, Player

def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    events = ClubEvent.objects.filter(club=club).order_by('-date')
    tournaments = Tournament.objects.filter(club=club).order_by('-start_date')
    players = Player.objects.filter(club=club).order_by('-rating')

    for player in players:
        stats = player.get_stats()
        stats['win_percent'] = round((stats['wins'] / stats['total_games']) * 100, 1) if stats['total_games'] > 0 else 0
        player.stats = stats

    context = {
        'club': club,
        'events': events,
        'tournaments': tournaments,
        'players': players,
    }

    return render(request, 'club_detail.html', context)



from django.contrib.auth.decorators import login_required
from .models import Club, ClubMembership
from django import forms

class CreateClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name']
        labels = {'name': 'Название клуба'}

@login_required
def create_club(request):
    if request.method == 'POST':
        form = CreateClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            ClubMembership.objects.create(user=request.user, club=club, is_active=True)
            return redirect('tennis_app:club_detail', club_id=club.id)
    else:
        form = CreateClubForm()

    return render(request, 'create_club.html', {'form': form})


from django.shortcuts import get_object_or_404, render, redirect
from .models import ClubMembership, Club

def my_club(request):
    if not request.user.is_authenticated:
        return redirect('tennis_app:login_register')

    membership = ClubMembership.objects.filter(user=request.user, is_active=True).first()

    if membership:
        return redirect('tennis_app:club_detail', club_id=membership.club.id)
    else:
        return render(request, 'no_club.html')  # шаблон с предложением создать клуб
    




from .forms import TournamentForm, ClubEventForm, PlayerForm

@login_required
def add_tournament(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.club = club
            tournament.created_by = request.user
            tournament.save()
            return redirect('tennis_app:club_detail', club_id=club.id)
    else:
        form = TournamentForm()
    return render(request, 'add_tournament.html', {'form': form, 'club': club})


@login_required
def add_event(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.method == 'POST':
        form = ClubEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            event.created_by = request.user
            event.save()
            return redirect('tennis_app:club_detail', club_id=club.id)
    else:
        form = ClubEventForm()
    return render(request, 'add_event.html', {'form': form, 'club': club})


@login_required
def add_player(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.club = club
            player.save()
            return redirect('tennis_app:club_detail', club_id=club.id)
    else:
        form = PlayerForm()
    return render(request, 'add_player.html', {'form': form, 'club': club})




from django.http import JsonResponse
from .models import FriendlyGame, Player, Club
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

@csrf_exempt
def save_friendly_game(request):
    if request.method == "POST":
        data = json.loads(request.body)

        name1 = data.get("player1")
        name2 = data.get("player2")
        winner_name = data.get("winner")

        score1 = data.get("score1", 0)
        score2 = data.get("score2", 0)

        # Находим игроков по имени, или создаем временных (если свободная игра)
        def get_or_create_player(name):
            player, _ = Player.objects.get_or_create(full_name=name, defaults={
                'club': None,  # свободный игрок
                'rating': 1000
            })
            return player

        player1 = get_or_create_player(name1)
        player2 = get_or_create_player(name2)
        winner = player1 if name1 == winner_name else player2

        game = FriendlyGame.objects.create(
            player1=player1,
            player2=player2,
            winner=winner,
            club=player1.club if player1.club == player2.club else None,
            played_at=now()
        )

        # можно добавить Game, если нужно сохранять партию

        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Invalid method"}, status=405)
