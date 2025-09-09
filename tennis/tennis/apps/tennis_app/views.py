from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json

from .forms import LoginForm, RegisterForm

# Create your views here.
def main(request):
    return render(request, 'home_index.html')

def demo_play(request):
    return render(request, 'demo_play.html')


# def friend_play(request):
#     club_id = request.GET.get("club_id")
#     players = []
#     if club_id:
#         try:
#             club = Club.objects.get(id=club_id)
#             players = Player.objects.filter(club=club).order_by("full_name")
#         except Club.DoesNotExist:
#             pass
#     return render(request, 'friend_play.html', {"players": players})


def my_tournaments(request):
    return render(request, 'my_tournaments.html')

def rules(request):
    return render(request, 'rules.html')

def settings_view(request):
    """Страница настроек интерфейса"""
    return render(request, 'settings.html')

def friend_play(request):
    user = request.user
    club_ids = Club.objects.filter(clubmembership__user=user, clubmembership__is_active=True).values_list('id', flat=True)

    if not club_ids:
        return redirect('tennis_app:main')  # или сообщение: вы не состоите в клубе

    club = Club.objects.get(id=club_ids[0])  # если пользователь состоит в нескольких — можно выбрать первым

    players = Player.objects.filter(club=club).order_by('full_name')

    return render(request, 'play_game.html', {
        'players': players,
        'club': club,
        'is_tournament': False,
        'title': 'Товарищеская партия',
        'header': 'Товарищеская партия',
    })








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

    # Флаг администратора клуба (кнопки добавления скрываем для не админов / неавторизованных)
    from .models import ClubAdmin  # локальный импорт чтобы избежать циклов при старте
    is_club_admin = False
    if request.user.is_authenticated:
        is_club_admin = ClubAdmin.objects.filter(user=request.user, club=club).exists()

    context = {
        'club': club,
        'events': events,
        'tournaments': tournaments,
        'players': players,
        'is_club_admin': is_club_admin,
    }

    return render(request, 'club_detail.html', context)


def player_detail(request, player_id):
    """Страница статистики игрока: сверху общая статистика, ниже — список игроков клуба с H2H."""
    player = get_object_or_404(Player.objects.select_related('club'), id=player_id)
    club = player.club

    # Общая статистика игрока (используем существующий метод)
    overall = player.get_stats()
    overall['win_percent'] = round((overall['wins'] / overall['total_games']) * 100, 1) if overall.get('total_games') else 0

    # Head-to-head по игрокам клуба
    from django.db.models import Q
    from .models import Match, FriendlyGame

    club_players = list(Player.objects.filter(club=club).exclude(id=player.id).order_by('full_name'))
    h2h_rows = []

    # Собираем одиночные товарищеские и матчи, где оба игрока заданы
    for opp in club_players:
        # Матчи турниров между player и opp
        matches = Match.objects.filter(
            Q(player1__in=[player, opp]) & Q(player2__in=[player, opp])
        )
        # Одиночные товарищеские между player и opp
        friend_single = FriendlyGame.objects.filter(
            game_type='single'
        ).filter(
            (Q(player1=player) & Q(player2=opp)) | (Q(player1=opp) & Q(player2=player))
        )

        # Парные товарищеские: считаем, если они были в одной из команд с кем-то против кого-то из команды соперника
        # Для H2H считаем игру, если оба игрока участвовали и были в разных командах
        friend_double = FriendlyGame.objects.filter(game_type='double').filter(
            (
                (Q(team1_player1=player) | Q(team1_player2=player)) &
                (Q(team2_player1=opp) | Q(team2_player2=opp))
            ) | (
                (Q(team2_player1=player) | Q(team2_player2=player)) &
                (Q(team1_player1=opp) | Q(team1_player2=opp))
            )
        )

        total = matches.count() + friend_single.count() + friend_double.count()

        # Считаем только завершенные для вин/лосс и процента
        finished_matches = matches.exclude(winner__isnull=True)
        finished_friend_single = friend_single.exclude(winner__isnull=True)
        finished_friend_double = friend_double.exclude(winning_team__isnull=True)
        completed = (
            finished_matches.count() +
            finished_friend_single.count() +
            finished_friend_double.count()
        )

        # Победы игрока
        wins = 0
        wins += finished_matches.filter(winner=player).count()
        wins += finished_friend_single.filter(winner=player).count()
        # Победы в парных — по winning_team
        wins += FriendlyGame.objects.filter(id__in=finished_friend_double.values('id')).filter(
            (
                (Q(team1_player1=player) | Q(team1_player2=player)) & Q(winning_team=1)
            ) | (
                (Q(team2_player1=player) | Q(team2_player2=player)) & Q(winning_team=2)
            )
        ).count()

        losses = completed - wins
        win_pct = round((wins / completed) * 100, 1) if completed else 0
        h2h_rows.append({
            'opponent': opp,
            'games': total,
            'wins': wins,
            'losses': losses,
            'win_pct': win_pct,
        })

    # Сортировка по количеству игр, затем по названию
    h2h_rows.sort(key=lambda r: (-r['games'], r['opponent'].full_name.lower()))

    # Получаем все игры игрока для списка игр с деталями
    all_games = []
    
    # Турнирные матчи
    tournament_matches = Match.objects.filter(
        Q(player1=player) | Q(player2=player)
    ).select_related('tournament', 'player1', 'player2', 'winner').order_by('-played_at')
    
    for match in tournament_matches:
        opponent = match.player2 if match.player1 == player else match.player1
        # Определяем результат
        if match.winner == player:
            result = 'Победа'
            result_class = 'win'
        elif match.winner is not None:
            result = 'Поражение'
            result_class = 'loss'
        else:
            result = 'Не завершен'
            result_class = 'incomplete'
        
        # Определяем судью (того, кто сохранил результат)
        referee = match.tournament.created_by.username if match.tournament.created_by else 'Система'
        
        all_games.append({
            'date': match.played_at,
            'type': 'tournament',
            'tournament_name': match.tournament.name,
            'opponent': opponent.full_name if opponent else 'TBA',
            'score': f"{match.sets_player1}:{match.sets_player2}" if match.finished else 'В процессе',
            'result': result,
            'result_class': result_class,
            'referee': referee
        })
    
    # Одиночные товарищеские игры
    friendly_singles = FriendlyGame.objects.filter(
        game_type='single'
    ).filter(
        Q(player1=player) | Q(player2=player)
    ).select_related('player1', 'player2', 'winner', 'recorded_by').order_by('-played_at')
    
    for friendly in friendly_singles:
        opponent = friendly.player2 if friendly.player1 == player else friendly.player1
        
        # Определяем результат
        if friendly.winner == player:
            result = 'Победа'
            result_class = 'win'
        elif friendly.winner is not None:
            result = 'Поражение'
            result_class = 'loss'
        else:
            result = 'Не завершена'
            result_class = 'incomplete'
        
        # Определяем счет для одиночных игр
        if friendly.player1 == player:
            score = f"{friendly.score_team1}:{friendly.score_team2}"
        else:
            score = f"{friendly.score_team2}:{friendly.score_team1}"
        
        # Определяем судью
        referee = friendly.recorded_by.username if friendly.recorded_by else 'Н/Д'
        
        all_games.append({
            'date': friendly.played_at,
            'type': 'friendly_single',
            'tournament_name': 'Товарищеская (одиночная)',
            'opponent': opponent.full_name if opponent else 'Неизвестно',
            'score': score if friendly.score_team1 > 0 or friendly.score_team2 > 0 else 'Н/Д',
            'result': result,
            'result_class': result_class,
            'referee': referee
        })
    
    # Парные товарищеские игры
    friendly_doubles = FriendlyGame.objects.filter(
        game_type='double'
    ).filter(
        Q(team1_player1=player) | Q(team1_player2=player) | 
        Q(team2_player1=player) | Q(team2_player2=player)
    ).select_related('team1_player1', 'team1_player2', 'team2_player1', 'team2_player2', 'recorded_by').order_by('-played_at')
    
    for friendly in friendly_doubles:
        # Определяем команду игрока и команду соперника
        if friendly.team1_player1 == player or friendly.team1_player2 == player:
            player_team = 1
            partner = friendly.team1_player2 if friendly.team1_player1 == player else friendly.team1_player1
            opponents = [friendly.team2_player1, friendly.team2_player2]
            score = f"{friendly.score_team1}:{friendly.score_team2}"
        else:
            player_team = 2
            partner = friendly.team2_player2 if friendly.team2_player1 == player else friendly.team2_player1
            opponents = [friendly.team1_player1, friendly.team1_player2]
            score = f"{friendly.score_team2}:{friendly.score_team1}"
        
        # Формируем строку с соперниками
        opponent_names = " / ".join([p.full_name for p in opponents if p])
        partner_name = partner.full_name if partner else 'Неизвестно'
        
        # Определяем результат
        if friendly.winning_team == player_team:
            result = 'Победа'
            result_class = 'win'
        elif friendly.winning_team is not None:
            result = 'Поражение'
            result_class = 'loss'
        else:
            result = 'Не завершена'
            result_class = 'incomplete'
        
        # Определяем судью
        referee = friendly.recorded_by.username if friendly.recorded_by else 'Н/Д'
        
        all_games.append({
            'date': friendly.played_at,
            'type': 'friendly_double',
            'tournament_name': 'Товарищеская (парная)',
            'opponent': f"{opponent_names} (партнер: {partner_name})",
            'score': score if friendly.score_team1 > 0 or friendly.score_team2 > 0 else 'Н/Д',
            'result': result,
            'result_class': result_class,
            'referee': referee
        })
    
    # Сортируем все игры по дате (новые первые)
    all_games.sort(key=lambda x: x['date'], reverse=True)
    
    # Пагинация для списка игр
    page_number = request.GET.get('page', 1)
    paginator = Paginator(all_games, 10)  # 10 игр на страницу
    games_page = paginator.get_page(page_number)

    return render(request, 'player_detail.html', {
        'player': player,
        'club': club,
        'overall': overall,
        'h2h_rows': h2h_rows,
        'games_page': games_page,
    })


from django.http import JsonResponse

def player_monthly_stats(request, player_id):
    """API endpoint для получения месячной статистики игрока"""
    try:
        player = get_object_or_404(Player, id=player_id)
        year = request.GET.get('year')
        
        if year:
            try:
                year = int(year)
            except ValueError:
                return JsonResponse({'error': 'Неверный формат года'}, status=400)
        
        monthly_stats = player.get_monthly_stats(year)
        
        return JsonResponse({
            'player_name': player.full_name,
            'year': year or timezone.now().year,
            'monthly_stats': monthly_stats
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



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
            # Назначаем создателя администратором клуба, если ещё нет админов
            from .models import ClubAdmin
            if not ClubAdmin.objects.filter(club=club, user=request.user).exists():
                ClubAdmin.objects.create(club=club, user=request.user)
            return redirect('tennis_app:club_detail', club_id=club.id)
    else:
        form = CreateClubForm()

    return render(request, 'create_club.html', {'form': form})


from django.shortcuts import get_object_or_404, render, redirect
from .models import ClubMembership, Club, ClubAdminInvite
from django.utils import timezone

def my_club(request):
    if not request.user.is_authenticated:
        return redirect('tennis_app:login_register')

    membership = ClubMembership.objects.filter(user=request.user, is_active=True).select_related('club').first()

    if membership:
        return redirect('tennis_app:club_detail', club_id=membership.club.id)
    else:
        # Показываем активные приглашения (по email пользователя)
        invites = []
        if request.user.email:
            invites = list(
                ClubAdminInvite.objects.filter(
                    email__iexact=request.user.email,
                    is_active=True,
                ).select_related('club')
            )
            now_ts = timezone.now()
            # Отфильтровать просроченные (и деактивировать их лениво)
            valid_invites = []
            for inv in invites:
                if inv.expires_at and inv.expires_at < now_ts:
                    if inv.is_active:
                        inv.is_active = False
                        inv.save(update_fields=['is_active'])
                else:
                    valid_invites.append(inv)
            invites = valid_invites
        return render(request, 'no_club.html', {"invites": invites})  # шаблон с приглашениями если есть
    




from .forms import TournamentForm, ClubEventForm, PlayerForm, TournamentParticipantForm, AdminInviteForm, AcceptInviteForm, TournamentMatchForm
from .models import TournamentParticipant, Match, Standing, ClubAdminInvite, ClubAdmin, Point

@login_required
def add_tournament(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    from .models import ClubAdmin
    if not ClubAdmin.objects.filter(user=request.user, club=club).exists():
        messages.error(request, 'Недостаточно прав')
        return redirect('tennis_app:club_detail', club_id=club.id)
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.club = club
            tournament.created_by = request.user
            tournament.save()
            # Создаем standings для кругового турнира сразу
            if tournament.tournament_type == tournament.ROUND_ROBIN:
                for player in Player.objects.filter(club=club):
                    Standing.objects.get_or_create(tournament=tournament, player=player)
            return redirect('tennis_app:club_detail', club_id=club.id)
    else:
        form = TournamentForm()
    return render(request, 'add_tournament.html', {'form': form, 'club': club})


@login_required
def add_event(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    from .models import ClubAdmin
    if not ClubAdmin.objects.filter(user=request.user, club=club).exists():
        messages.error(request, 'Недостаточно прав')
        return redirect('tennis_app:club_detail', club_id=club.id)
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
    from .models import ClubAdmin
    if not ClubAdmin.objects.filter(user=request.user, club=club).exists():
        messages.error(request, 'Недостаточно прав')
        return redirect('tennis_app:club_detail', club_id=club.id)
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


# ------------------ Турниры расширенно ------------------

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    participants = list(TournamentParticipant.objects.filter(tournament=tournament).select_related('player'))
    matches = list(tournament.matches.select_related('player1','player2','winner').all())
    standings = tournament.standings.select_related('player').order_by('rank') if tournament.tournament_type == Tournament.ROUND_ROBIN else []

    # Форма создания матча вручную
    match_form = TournamentMatchForm()
    if request.method == 'POST' and 'create_match' in request.POST:
        from .models import ClubAdmin
        if not (request.user.is_authenticated and ClubAdmin.objects.filter(user=request.user, club=tournament.club).exists()):
            messages.error(request, 'Недостаточно прав')
            return redirect('tennis_app:tournament_detail', tournament_id=tournament.id)
        match_form = TournamentMatchForm(request.POST)
        # Ограничим выбор списком участников
        allowed_players = Player.objects.filter(tournamentparticipant__tournament=tournament)
        match_form.fields['player1'].queryset = allowed_players
        match_form.fields['player2'].queryset = allowed_players
        
        # Получаем player1 и player2 из формы
        player1_id = request.POST.get('player1')
        player2_id = request.POST.get('player2')
        
        try:
            player1 = Player.objects.get(id=player1_id, tournamentparticipant__tournament=tournament)
            player2 = Player.objects.get(id=player2_id, tournamentparticipant__tournament=tournament)
            
            if player1.id == player2.id:
                messages.error(request, 'Игроки должны быть разными')
            else:
                # Проверяем, что матча между этими игроками еще нет
                existing_match = Match.objects.filter(
                    tournament=tournament,
                    player1__in=[player1, player2],
                    player2__in=[player1, player2]
                ).first()
                
                if existing_match:
                    messages.error(request, 'Матч между этими игроками уже существует')
                else:
                    # Создаем новый матч
                    new_match = Match.objects.create(
                        tournament=tournament,
                        player1=player1,
                        player2=player2,
                        round_number=1  # для круговых турниров всегда 1
                    )
                    messages.success(request, f'Матч создан: {player1.full_name} vs {player2.full_name}')
                    return redirect('tennis_app:tournament_detail', tournament_id=tournament.id)
                    
        except Player.DoesNotExist:
            messages.error(request, 'Неверные игроки')
        except Exception as e:
            messages.error(request, f'Ошибка создания матча: {str(e)}')
            
        return redirect('tennis_app:tournament_detail', tournament_id=tournament.id)
    else:
        allowed_players = Player.objects.filter(tournamentparticipant__tournament=tournament)
        match_form.fields['player1'].queryset = allowed_players
        match_form.fields['player2'].queryset = allowed_players

    # Матрица результатов для кругового турнира
    rr_matrix = []
    if tournament.tournament_type == Tournament.ROUND_ROBIN and participants:
        players_order = [p.player for p in participants]
        # Создаем словарь результатов: (p1_id, p2_id) -> {winner_id, sets_score, match_obj}
        result_map = {}
        for m in matches:
            if m.player1_id and m.player2_id:
                key = (m.player1_id, m.player2_id)
                sets_score = f"{m.sets_player1}:{m.sets_player2}" if m.finished else f"{m.sets_player1}:{m.sets_player2}"
                result_map[key] = {
                    'winner_id': m.winner_id,
                    'sets_score': sets_score,
                    'match': m
                }
                key_rev = (m.player2_id, m.player1_id)
                # Для обратного направления победитель тот же, но счет обратный
                sets_score_rev = f"{m.sets_player2}:{m.sets_player1}" if m.finished else f"{m.sets_player2}:{m.sets_player1}"
                result_map[key_rev] = {
                    'winner_id': m.winner_id,
                    'sets_score': sets_score_rev,
                    'match': m
                }
        
        for row_player in players_order:
            row = []
            for col_player in players_order:
                if row_player.id == col_player.id:
                    cell = {
                        'status': '—',
                        'sets_score': '',
                        'opponent_id': col_player.id,
                        'match_id': None
                    }
                else:
                    match_data = result_map.get((row_player.id, col_player.id))
                    if match_data is None:
                        # Матча нет
                        cell = {
                            'status': '',
                            'sets_score': '',
                            'opponent_id': col_player.id,
                            'match_id': None
                        }
                    elif match_data['winner_id'] is None:
                        # Матч есть, но не завершен
                        cell = {
                            'status': 'P',  # В процессе
                            'sets_score': match_data['sets_score'],
                            'opponent_id': col_player.id,
                            'match_id': match_data['match'].id
                        }
                    elif match_data['winner_id'] == row_player.id:
                        cell = {
                            'status': 'W',
                            'sets_score': match_data['sets_score'],
                            'opponent_id': col_player.id,
                            'match_id': match_data['match'].id
                        }
                    else:
                        cell = {
                            'status': 'L',
                            'sets_score': match_data['sets_score'],
                            'opponent_id': col_player.id,
                            'match_id': match_data['match'].id
                        }
                row.append(cell)
            rr_matrix.append({'player': row_player, 'results': row})

    # Флаг администратора клуба турнира
    from .models import ClubAdmin
    is_club_admin = False
    if request.user.is_authenticated:
        is_club_admin = ClubAdmin.objects.filter(user=request.user, club=tournament.club).exists()

    return render(request, 'tournament_detail.html', {
        'tournament': tournament,
        'participants': participants,
        'matches': matches,
        'standings': standings,
        'match_form': match_form,
        'rr_matrix': rr_matrix,
        'is_club_admin': is_club_admin,
    })


@login_required
def add_participant(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    from .models import ClubAdmin
    if not ClubAdmin.objects.filter(user=request.user, club=tournament.club).exists():
        messages.error(request, 'Недостаточно прав')
        return redirect('tennis_app:tournament_detail', tournament_id=tournament.id)
    if request.method == 'POST':
        form = TournamentParticipantForm(request.POST)
        if form.is_valid():
            tp = form.save(commit=False)
            tp.tournament = tournament
            if tp.player.club != tournament.club:
                messages.error(request, 'Игрок должен принадлежать клубу турнира')
            else:
                tp.save()
                if tournament.tournament_type == Tournament.ROUND_ROBIN:
                    Standing.objects.get_or_create(tournament=tournament, player=tp.player)
            return redirect('tennis_app:tournament_detail', tournament_id=tournament.id)
    else:
        form = TournamentParticipantForm()
        form.fields['player'].queryset = Player.objects.filter(club=tournament.club)
    return render(request, 'add_participant.html', {'form': form, 'tournament': tournament})


@login_required
def generate_matches(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    from .models import ClubAdmin
    if not ClubAdmin.objects.filter(user=request.user, club=tournament.club).exists():
        messages.error(request, 'Недостаточно прав')
        return redirect('tennis_app:tournament_detail', tournament_id=tournament.id)
    tournament.generate_matches()
    return redirect('tennis_app:tournament_detail', tournament_id=tournament.id)


@login_required
def report_match_result(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    from .models import ClubAdmin
    if not ClubAdmin.objects.filter(user=request.user, club=match.tournament.club).exists():
        messages.error(request, 'Недостаточно прав')
        return redirect('tennis_app:tournament_detail', tournament_id=match.tournament.id)
    if request.method == 'POST':
        winner_id = request.POST.get('winner')
        try:
            winner = Player.objects.get(id=winner_id)
            if winner not in [match.player1, match.player2]:
                raise ValueError
            match.set_winner(winner)
            messages.success(request, 'Результат сохранен')
        except Exception:
            messages.error(request, 'Ошибка сохранения результата')
        return redirect('tennis_app:tournament_detail', tournament_id=match.tournament.id)
    return render(request, 'report_match_result.html', {'match': match})


@login_required
def play_match_live(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    from .models import ClubAdmin
    if not ClubAdmin.objects.filter(user=request.user, club=match.tournament.club).exists():
        messages.error(request, 'Недостаточно прав')
        return redirect('tennis_app:tournament_detail', tournament_id=match.tournament.id)
    if not (match.player1 and match.player2):
        messages.error(request, 'Невозможно начать: не оба игрока заданы')
        return redirect('tennis_app:tournament_detail', tournament_id=match.tournament.id)
    
    # Получаем текущую партию (последняя незавершенная)
    current_game = match.get_current_game()
    
    # Получаем все завершенные партии для отображения истории
    completed_games = match.get_completed_games()

    if request.method == 'POST':
        action = request.POST.get('action')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        response_data = {
            'success': False,
            'message': '',
            'message_type': 'info',
            'match_finished': False,
            'set_finished': False,
            'current_game': bool(current_game),
            'score': [0, 0],
            'sets': {'p1': match.sets_player1, 'p2': match.sets_player2},
            'player1_name': match.player1.full_name,
            'player2_name': match.player2.full_name,
            'first_server': current_game.first_server if current_game else 1
        }
        
        # Начало новой партии
        if action == 'start_set' and not current_game and not match.finished:
            first_server = int(request.POST.get('first_server', 1))  # По умолчанию первый игрок
            from django.utils import timezone
            current_game = Game.objects.create(
                match=match,
                start_time=timezone.now(),
                first_server=first_server
            )
            response_data['success'] = True
            response_data['message'] = 'Новая партия начата!'
            response_data['current_game'] = True
            response_data['set_finished'] = True  # Чтобы обновить страницу
            
        elif action in ['p1', 'p2'] and current_game and not match.finished:
            # Добавление очка
            scorer = match.player1 if action == 'p1' else match.player2
            order = current_game.points.count() + 1
            Point.objects.create(game=current_game, scored_by=scorer, order=order)
            current_game.recalculate_score()
            
            response_data['success'] = True
            response_data['score'] = [current_game.score_player1, current_game.score_player2]
            response_data['message'] = f'Очко для {scorer.full_name}!'
            
            # Проверяем завершение партии (до 11 с разницей >=2)
            s1, s2 = current_game.score_player1, current_game.score_player2
            if (s1 >= 11 or s2 >= 11) and abs(s1 - s2) >= 2:
                # Партия завершена
                from django.utils import timezone
                current_game.end_time = timezone.now()
                current_game.save(update_fields=['end_time'])
                
                # Начисляем сет победителю партии
                if s1 > s2:
                    match.sets_player1 += 1
                    response_data['message'] = f'Партия завершена! Победитель: {match.player1.full_name} ({s1}:{s2})'
                    response_data['message_type'] = 'success'
                else:
                    match.sets_player2 += 1
                    response_data['message'] = f'Партия завершена! Победитель: {match.player2.full_name} ({s2}:{s1})'
                    response_data['message_type'] = 'success'
                
                match.save(update_fields=['sets_player1','sets_player2'])
                response_data['sets'] = {'p1': match.sets_player1, 'p2': match.sets_player2}
                response_data['set_finished'] = True
                
                # Проверка победы в матче (до 2 выигранных партий)
                if match.sets_player1 == 2:
                    match.set_winner(match.player1)
                    match.finished = True
                    match.save(update_fields=['finished'])
                    response_data['message'] = f'Матч завершен! Победитель: {match.player1.full_name} (2:{match.sets_player2})'
                    response_data['match_finished'] = True
                elif match.sets_player2 == 2:
                    match.set_winner(match.player2)
                    match.finished = True
                    match.save(update_fields=['finished'])
                    response_data['message'] = f'Матч завершен! Победитель: {match.player2.full_name} (2:{match.sets_player1})'
                    response_data['match_finished'] = True
                else:
                    # Матч продолжается, партия завершена
                    current_game = None
                    response_data['current_game'] = False
                    
        elif action in ['undo_p1', 'undo_p2'] and current_game and not match.finished:
            # Откат последнего очка
            scorer = match.player1 if action == 'undo_p1' else match.player2
            last_point = current_game.points.filter(scored_by=scorer).order_by('-order').first()
            if last_point:
                last_point.delete()
                current_game.recalculate_score()
                response_data['success'] = True
                response_data['score'] = [current_game.score_player1, current_game.score_player2]
                response_data['message'] = f'Очко отменено для {scorer.full_name}'
                response_data['message_type'] = 'info'
            else:
                response_data['message'] = f'Нет очков для отмены у {scorer.full_name}'
                response_data['message_type'] = 'error'
                    
        elif action == 'new_set' and not current_game and not match.finished:
            first_server = int(request.POST.get('first_server', 1))  # По умолчанию первый игрок
            from django.utils import timezone
            current_game = Game.objects.create(
                match=match,
                start_time=timezone.now(),
                first_server=first_server
            )
            response_data['success'] = True
            response_data['message'] = 'Новая партия начата!'
            response_data['current_game'] = True
            response_data['set_finished'] = True  # Чтобы обновить страницу
        
        # Если это AJAX запрос, возвращаем JSON
        if is_ajax:
            if not response_data['success'] and not response_data['message']:
                response_data['message'] = 'Неизвестная ошибка'
                response_data['message_type'] = 'error'
            return JsonResponse(response_data)
        else:
            # Обычное поведение с перенаправлением
            if response_data['message']:
                if response_data['message_type'] == 'success':
                    messages.success(request, response_data['message'])
                elif response_data['message_type'] == 'error':
                    messages.error(request, response_data['message'])
                else:
                    messages.info(request, response_data['message'])
            return redirect('tennis_app:play_match_live', match_id=match.id)

    # Подготовка данных для шаблона
    sets = {
        'p1': match.sets_player1,
        'p2': match.sets_player2,
    }
    score = (current_game.score_player1, current_game.score_player2) if current_game else (0,0)
    
    # Подготовка истории партий
    games_history = []
    for game in completed_games:
        games_history.append({
            'score_p1': game.score_player1,
            'score_p2': game.score_player2,
            'winner': game.get_winner()
        })
    
    return render(request, 'play_match_live.html', {
        'match': match,
        'current_game': current_game,
        'score': score,
        'sets': sets,
        'games_history': games_history,
        'is_tournament': True,
        'title': 'Живой матч',
        'header': f'Матч: {match.player1.full_name} vs {match.player2.full_name}',
    })


# ------------------ Приглашения администраторов ------------------

@login_required
def invite_admin(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    # Проверка прав: только администратор клуба может приглашать других администраторов
    from .models import ClubAdmin
    if not ClubAdmin.objects.filter(user=request.user, club=club).exists():
        messages.error(request, 'Недостаточно прав')
        return redirect('tennis_app:club_detail', club_id=club.id)
    if request.method == 'POST':
        form = AdminInviteForm(request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.club = club
            invite.invited_by = request.user
            invite.save()
            messages.success(request, f'Приглашение создано. Токен: {invite.token}')
            return redirect('tennis_app:club_detail', club_id=club.id)
    else:
        form = AdminInviteForm()
    invites = club.admin_invites.order_by('-created_at')[:20]
    return render(request, 'invite_admin.html', {'form': form, 'club': club, 'invites': invites})


@login_required
def accept_invite(request):
    if request.method == 'POST':
        form = AcceptInviteForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            invite = ClubAdminInvite.objects.filter(token=token, is_active=True).first()
            if invite and invite.accept(request.user):
                messages.success(request, f'Вы стали администратором клуба {invite.club.name}')
                return redirect('tennis_app:club_detail', club_id=invite.club.id)
            else:
                messages.error(request, 'Недействительное или просроченное приглашение')
    else:
        form = AcceptInviteForm()
    return render(request, 'accept_invite.html', {'form': form})


@login_required
def accept_invite_direct(request, invite_id):
    """Прямое принятие приглашения без ввода токена (кнопка на странице 'Мой клуб')."""
    invite = ClubAdminInvite.objects.filter(id=invite_id, is_active=True).select_related('club').first()
    if not invite:
        messages.error(request, 'Приглашение не найдено или уже не активно')
        return redirect('tennis_app:my_club')
    # Проверяем email совпадение
    if request.user.email and request.user.email.lower() != invite.email.lower():
        messages.error(request, 'Email пользователя не совпадает с email приглашения')
        return redirect('tennis_app:my_club')
    if invite.expires_at and timezone.now() > invite.expires_at:
        invite.is_active = False
        invite.save(update_fields=['is_active'])
        messages.error(request, 'Приглашение истекло')
        return redirect('tennis_app:my_club')
    if invite.accept(request.user):
        messages.success(request, f'Вы стали администратором клуба {invite.club.name}')
        return redirect('tennis_app:club_detail', club_id=invite.club.id)
    messages.error(request, 'Не удалось принять приглашение')
    return redirect('tennis_app:my_club')




from django.http import JsonResponse
from .models import FriendlyGame, Player, Club
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

from .models import Game

@csrf_exempt
def save_friendly_game(request):
    if request.method == "POST":
        data = json.loads(request.body)
        game_type = data.get("game_type", "single")
        score1 = data.get("score1", 0)
        score2 = data.get("score2", 0)
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        def get_or_create_player(name):
            if not name:
                return None
            player, _ = Player.objects.get_or_create(full_name=name, defaults={'club': None, 'rating': 1000})
            return player

        if game_type == 'single':
            name1 = data.get("player1")
            name2 = data.get("player2")
            winner_name = data.get("winner")
            player1 = get_or_create_player(name1)
            player2 = get_or_create_player(name2)
            winner = player1 if name1 == winner_name else player2
            game_obj = FriendlyGame.objects.create(
                game_type='single',
                player1=player1,
                player2=player2,
                winner=winner,
                club=player1.club if (player1 and player2 and player1.club == player2.club) else None,
                played_at=end_time,
                score_team1=score1,
                score_team2=score2,
                recorded_by=request.user if request.user.is_authenticated else None
            )
        else:  # double
            t1p1 = get_or_create_player(data.get("team1_player1"))
            t1p2 = get_or_create_player(data.get("team1_player2"))
            t2p1 = get_or_create_player(data.get("team2_player1"))
            t2p2 = get_or_create_player(data.get("team2_player2"))
            winning_team = data.get("winning_team")  # 1 или 2
            # Определим клуб (если все игроки в одном клубе и он одинаковый)
            clubs = {p.club for p in [t1p1, t1p2, t2p1, t2p2] if p and p.club}
            club = clubs.pop() if len(clubs) == 1 else None
            game_obj = FriendlyGame.objects.create(
                game_type='double',
                player1=t1p1,  # для совместимости оставим один слот
                player2=t2p1,  # для совместимости
                club=club,
                team1_player1=t1p1,
                team1_player2=t1p2,
                team2_player1=t2p1,
                team2_player2=t2p2,
                winning_team=winning_team,
                played_at=end_time,
                score_team1=score1,
                score_team2=score2,
                recorded_by=request.user if request.user.is_authenticated else None
            )

        Game.objects.create(
            friendly=game_obj,
            start_time=start_time,
            end_time=end_time,
            score_player1=score1,
            score_player2=score2
        )

        return JsonResponse({"status": "ok", "game_type": game_type})
    return JsonResponse({"error": "Invalid method"}, status=405)
