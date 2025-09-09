from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
import math, secrets


class Club(models.Model):
    name = models.CharField("Название клуба", max_length=100, unique=True)

    class Meta:
        verbose_name = "Клуб"
        verbose_name_plural = "Клубы"

    def __str__(self):
        return self.name

    @property
    def admins(self):
        return User.objects.filter(clubadmin__club=self)


class ClubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Клуб")
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        unique_together = ('user', 'club')
        verbose_name = "Член клуба"
        verbose_name_plural = "Члены клуба"


class ClubAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Клуб")
    assigned_at = models.DateTimeField("Назначен", auto_now_add=True)

    class Meta:
        unique_together = ('user', 'club')
        verbose_name = "Администратор клуба"
        verbose_name_plural = "Администраторы клуба"


class Player(models.Model):
    full_name = models.CharField("ФИО", max_length=100)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Клуб")
    joined_at = models.DateTimeField("Дата вступления", auto_now_add=True)
    rating = models.IntegerField("Рейтинг", default=1000)
    dominant_hand = models.CharField("Преобладающая рука", max_length=10, choices=[('right', 'Правая'), ('left', 'Левая')], default='right')

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"

    def __str__(self):
        return self.full_name

    def get_stats(self):
        matches = Match.objects.filter(models.Q(player1=self) | models.Q(player2=self))
        # Одиночные товарищеские
        friendlies_single = FriendlyGame.objects.filter(game_type='single').filter(models.Q(player1=self) | models.Q(player2=self))
        # Парные товарищеские (искать во всех слотах команды)
        friendlies_double = FriendlyGame.objects.filter(game_type='double').filter(
            models.Q(team1_player1=self) | models.Q(team1_player2=self) | models.Q(team2_player1=self) | models.Q(team2_player2=self)
        )
        friendlies = friendlies_single.union(friendlies_double)
        match_wins = matches.filter(winner=self).count()
        # Победы в одиночных как раньше + победы в парных, где его команда выиграла
        friendly_single_wins = friendlies_single.filter(winner=self).count()
        friendly_double_wins = FriendlyGame.objects.filter(game_type='double', winning_team__isnull=False).filter(
            (
                (models.Q(team1_player1=self) | models.Q(team1_player2=self)) & models.Q(winning_team=1)
            ) | (
                (models.Q(team2_player1=self) | models.Q(team2_player2=self)) & models.Q(winning_team=2)
            )
        ).count()
        friendly_wins = friendly_single_wins + friendly_double_wins
        total_points = Point.objects.filter(scored_by=self).count()
        games = Game.objects.filter(models.Q(match__player1=self) | models.Q(match__player2=self) |
                                     models.Q(friendly__player1=self) | models.Q(friendly__player2=self) |
                                     models.Q(friendly__team1_player1=self) | models.Q(friendly__team1_player2=self) |
                                     models.Q(friendly__team2_player1=self) | models.Q(friendly__team2_player2=self))
        return {
            'matches': matches.count(),
            'friendlies': friendlies.count(),  # общее число товарищеских (single + double)
            'total_games': matches.count() + friendlies.count(),
            'total_parties': games.count(),
            'wins': match_wins + friendly_wins,
            # Поражения: одиночные где не winner + парные где его команда проиграла
            'losses': (
                matches.exclude(winner=self).count() +
                friendlies_single.exclude(winner=self).count() +
                FriendlyGame.objects.filter(game_type='double', winning_team__isnull=False).filter(
                    (
                        (models.Q(team1_player1=self) | models.Q(team1_player2=self)) & models.Q(winning_team=2)
                    ) | (
                        (models.Q(team2_player1=self) | models.Q(team2_player2=self)) & models.Q(winning_team=1)
                    )
                ).count()
            ),
            'scored_points': total_points
        }

    def get_monthly_stats(self, year=None):
        """Получает статистику игрока по месяцам за указанный год"""
        from django.db.models import Q
        from datetime import datetime
        from collections import defaultdict
        
        if year is None:
            year = datetime.now().year
        
        # Инициализируем словарь для каждого месяца
        monthly_data = {}
        for month in range(1, 13):
            monthly_data[month] = {
                'month': month,
                'month_name': datetime(year, month, 1).strftime('%B'),
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'win_percent': 0
            }
        
        # Получаем все матчи игрока за год
        matches = Match.objects.filter(
            Q(player1=self) | Q(player2=self),
            played_at__year=year
        )
        
        # Получаем все товарищеские игры за год
        friendlies_single = FriendlyGame.objects.filter(
            game_type='single',
            played_at__year=year
        ).filter(Q(player1=self) | Q(player2=self))
        
        friendlies_double = FriendlyGame.objects.filter(
            game_type='double',
            played_at__year=year
        ).filter(
            Q(team1_player1=self) | Q(team1_player2=self) | 
            Q(team2_player1=self) | Q(team2_player2=self)
        )
        
        # Обрабатываем матчи турниров
        for match in matches:
            month = match.played_at.month
            monthly_data[month]['total_games'] += 1
            
            if match.winner == self:
                monthly_data[month]['wins'] += 1
            elif match.winner is not None:  # Матч завершен, но игрок проиграл
                monthly_data[month]['losses'] += 1
        
        # Обрабатываем одиночные товарищеские игры
        for friendly in friendlies_single:
            month = friendly.played_at.month
            monthly_data[month]['total_games'] += 1
            
            if friendly.winner == self:
                monthly_data[month]['wins'] += 1
            elif friendly.winner is not None:
                monthly_data[month]['losses'] += 1
        
        # Обрабатываем парные товарищеские игры
        for friendly in friendlies_double:
            month = friendly.played_at.month
            monthly_data[month]['total_games'] += 1
            
            if friendly.winning_team is not None:
                # Определяем, в какой команде играл игрок
                player_team = None
                if friendly.team1_player1 == self or friendly.team1_player2 == self:
                    player_team = 1
                elif friendly.team2_player1 == self or friendly.team2_player2 == self:
                    player_team = 2
                
                if player_team == friendly.winning_team:
                    monthly_data[month]['wins'] += 1
                else:
                    monthly_data[month]['losses'] += 1
        
        # Вычисляем процент побед для каждого месяца
        for month_data in monthly_data.values():
            completed_games = month_data['wins'] + month_data['losses']
            if completed_games > 0:
                month_data['win_percent'] = round((month_data['wins'] / completed_games) * 100, 1)
        
        return list(monthly_data.values())


class Tournament(models.Model):
    ROUND_ROBIN = 'round_robin'
    ELIMINATION = 'elimination'
    TOURNAMENT_TYPES = [
        (ROUND_ROBIN, 'Круговой'),
        (ELIMINATION, 'Олимпийка'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Клуб")
    name = models.CharField("Название турнира", max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Создатель")
    start_date = models.DateField("Дата начала")
    tournament_type = models.CharField("Тип турнира", max_length=20, choices=TOURNAMENT_TYPES, default=ROUND_ROBIN)
    created_at = models.DateTimeField("Создан", default=timezone.now)

    class Meta:
        verbose_name = "Турнир"
        verbose_name_plural = "Турниры"

    def __str__(self):
        return self.name

    @property
    def participants(self):
        return Player.objects.filter(tournamentparticipant__tournament=self)

    def generate_matches(self):
        """Генерация матчей для турнира в зависимости от типа."""
        if self.matches.exists():
            return  # Уже сгенерированы
        players = list(self.participants)
        if len(players) < 2:
            return
        if self.tournament_type == self.ROUND_ROBIN:
            # Каждый с каждым один раз
            for i in range(len(players)):
                for j in range(i + 1, len(players)):
                    Match.objects.create(tournament=self, player1=players[i], player2=players[j], round_number=1)
        else:  # ELIMINATION
            # Формируем олимпийскую сетку ближайшей степени двойки
            n = len(players)
            size = 1
            while size < n:
                size *= 2
            # Сортировка по seed если задан, иначе по id
            participants = list(TournamentParticipant.objects.filter(tournament=self).select_related('player').order_by('seed', 'id'))
            player_list = [p.player for p in participants]
            # Добавляем None для byes
            while len(player_list) < size:
                player_list.append(None)
            # Создаем первый раунд
            matches_current_round = []
            for i in range(0, size, 2):
                p1 = player_list[i]
                p2 = player_list[i+1]
                m = Match.objects.create(
                    tournament=self,
                    player1=p1 if p1 else player_list[i+1],  # временно, чтобы не было null обоих
                    player2=p2,
                    round_number=1,
                    bracket_position=i//2 + 1
                )
                matches_current_round.append(m)
                # Автовыигрыш при bye
                if p1 and not p2:
                    m.winner = p1
                    m.save()
                elif p2 and not p1:
                    m.winner = p2
                    m.save()
            # Создаем заготовки следующих раундов
            round_num = 2
            prev_round = matches_current_round
            while len(prev_round) > 1:
                next_round = []
                for idx in range(0, len(prev_round), 2):
                    m = Match.objects.create(
                        tournament=self,
                        player1=prev_round[idx].winner if prev_round[idx].winner else prev_round[idx].player1,
                        player2=prev_round[idx+1].winner if prev_round[idx+1].winner else prev_round[idx+1].player1,
                        round_number=round_num,
                        bracket_position=idx//2 + 1
                    )
                    prev_round[idx].next_match = m
                    prev_round[idx].save(update_fields=["next_match"])
                    prev_round[idx+1].next_match = m
                    prev_round[idx+1].save(update_fields=["next_match"])
                    next_round.append(m)
                prev_round = next_round
                round_num += 1

    def recalculate_standings(self):
        if self.tournament_type != self.ROUND_ROBIN:
            return
        # Simple win = 2 pts, loss = 0
        for standing in self.standings.all():
            standing.points = 0
            standing.save(update_fields=['points'])
        for match in self.matches.exclude(winner__isnull=True):
            st = Standing.objects.filter(tournament=self, player=match.winner).first()
            if st:
                st.points += 2
                st.save(update_fields=['points'])
        # Ранжирование
        ordered = self.standings.order_by('-points', 'player__full_name')
        for idx, st in enumerate(ordered, start=1):
            st.rank = idx
            st.save(update_fields=['rank'])


class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants_links', verbose_name="Турнир")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="Игрок")
    seed = models.PositiveIntegerField("Посев", default=0)
    joined_at = models.DateTimeField("Добавлен", auto_now_add=True)

    class Meta:
        unique_together = ('tournament', 'player')
        ordering = ['seed', 'id']
        verbose_name = "Участник турнира"
        verbose_name_plural = "Участники турнира"

    def __str__(self):
        return f"{self.player.full_name} ({self.tournament.name})"


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches', verbose_name="Турнир")
    player1 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_as_player1', verbose_name="Игрок 1")
    player2 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_as_player2', verbose_name="Игрок 2")
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='wins', verbose_name="Победитель")
    played_at = models.DateTimeField("Дата проведения", auto_now_add=True)
    round_number = models.PositiveIntegerField("Раунд", default=1)
    bracket_position = models.PositiveIntegerField("Позиция в раунде", null=True, blank=True)
    next_match = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_matches', verbose_name="Следующий матч")
    sets_player1 = models.PositiveIntegerField("Сеты игрока 1", default=0)
    sets_player2 = models.PositiveIntegerField("Сеты игрока 2", default=0)
    finished = models.BooleanField("Завершен", default=False)

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"
        ordering = ['round_number', 'bracket_position', 'id']

    def __str__(self):
        if self.finished:
            return f"{self.player1 or '-'} vs {self.player2 or '-'} ({self.sets_player1}:{self.sets_player2}) - Завершен"
        else:
            return f"{self.player1 or '-'} vs {self.player2 or '-'} ({self.sets_player1}:{self.sets_player2}) - В процессе"

    def set_winner(self, player: Player):
        self.winner = player
        self.save(update_fields=['winner'])
        # Если олимпийка — передаем победителя в следующий матч
        if self.tournament.tournament_type == Tournament.ELIMINATION and self.next_match:
            nm = self.next_match
            # Вставляем в свободный слот
            if nm.player1 is None or nm.player1 == self.player1 or nm.player1 == self.player2:
                nm.player1 = player if nm.player2 != player else nm.player1
            elif nm.player2 is None or nm.player2 == self.player1 or nm.player2 == self.player2:
                nm.player2 = player if nm.player1 != player else nm.player2
            nm.save()
        # Пересчет standings для кругового
        self.tournament.recalculate_standings()

    def get_match_status(self):
        """Возвращает строку с текущим статусом матча"""
        if self.finished:
            return f"Завершен ({self.sets_player1}:{self.sets_player2})"
        elif self.sets_player1 == 0 and self.sets_player2 == 0:
            return "Не начат"
        else:
            return f"В процессе ({self.sets_player1}:{self.sets_player2})"
    
    def get_current_game(self):
        """Возвращает текущую активную партию или None"""
        return self.games.filter(end_time__isnull=True).order_by('-created_at').first()
    
    def get_completed_games(self):
        """Возвращает все завершенные партии"""
        return self.games.exclude(end_time__isnull=True).order_by('created_at')


class Game(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='games', verbose_name="Матч", null=True, blank=True)
    friendly = models.ForeignKey('FriendlyGame', on_delete=models.CASCADE, related_name='games', verbose_name="Свободная игра", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    start_time = models.DateTimeField("Начало", null=True, blank=True)
    end_time = models.DateTimeField("Окончание", null=True, blank=True)
    score_player1 = models.PositiveIntegerField("Очки игрока 1", default=0)
    score_player2 = models.PositiveIntegerField("Очки игрока 2", default=0)
    first_server = models.PositiveIntegerField("Первый подающий", choices=[(1, 'Игрок 1'), (2, 'Игрок 2')], default=1)

    class Meta:
        verbose_name = "Партия"
        verbose_name_plural = "Партии"

    def clean(self):
        if bool(self.match) == bool(self.friendly):
            raise ValidationError("Партия должна быть связана либо с матчем, либо со свободной игрой, но не с обоими.")

    def get_score(self):
        return self.score_player1, self.score_player2

    def recalculate_score(self):
        if self.match:
            p1 = self.match.player1
            p2 = self.match.player2
        elif self.friendly:
            p1 = self.friendly.player1
            p2 = self.friendly.player2
        else:
            return
        self.score_player1 = self.points.filter(scored_by=p1).count()
        self.score_player2 = self.points.filter(scored_by=p2).count()
        self.save(update_fields=['score_player1', 'score_player2'])
    
    def get_winner(self):
        """Возвращает победителя партии или None если партия не завершена"""
        if self.end_time and self.score_player1 != self.score_player2:
            if self.match:
                return self.match.player1 if self.score_player1 > self.score_player2 else self.match.player2
            elif self.friendly:
                return self.friendly.player1 if self.score_player1 > self.score_player2 else self.friendly.player2
        return None


class FriendlyGame(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Клуб")
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='friendlies_as_player1', verbose_name="Игрок 1")
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='friendlies_as_player2', verbose_name="Игрок 2", null=True, blank=True)
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='friendly_wins', verbose_name="Победитель")
    played_at = models.DateTimeField("Дата проведения", auto_now_add=True)
    # Новые поля для парных игр
    GAME_TYPE_CHOICES = [
        ('single', 'Одиночная'),
        ('double', 'Парная'),
    ]
    game_type = models.CharField("Тип игры", max_length=10, choices=GAME_TYPE_CHOICES, default='single')
    # Составы команд для парной игры (необязательные, чтобы не ломать существующие данные)
    team1_player1 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='doubles_team1_p1', verbose_name="Команда 1 Игрок 1")
    team1_player2 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='doubles_team1_p2', verbose_name="Команда 1 Игрок 2")
    team2_player1 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='doubles_team2_p1', verbose_name="Команда 2 Игрок 1")
    team2_player2 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='doubles_team2_p2', verbose_name="Команда 2 Игрок 2")
    winning_team = models.PositiveSmallIntegerField("Победившая команда", choices=[(1, 'Команда 1'), (2, 'Команда 2')], null=True, blank=True)
    
    # Поля для счета и судьи
    score_team1 = models.PositiveIntegerField("Счет команды 1", default=0)
    score_team2 = models.PositiveIntegerField("Счет команды 2", default=0) 
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Записал результат")

    class Meta:
        verbose_name = "Свободная игра"
        verbose_name_plural = "Свободные игры"

    def __str__(self):
        if self.game_type == 'double':
            t1 = " / ".join([p.full_name for p in [self.team1_player1, self.team1_player2] if p]) or '—'
            t2 = " / ".join([p.full_name for p in [self.team2_player1, self.team2_player2] if p]) or '—'
            return f"{t1} vs {t2} (парная)"
        return f"{self.player1} vs {self.player2 or '—'} (одиночная)"


class Point(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='points', verbose_name="Партия")
    scored_by = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="Игрок, набравший очко")
    timestamp = models.DateTimeField("Время", auto_now_add=True)
    order = models.PositiveIntegerField("Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = "Очко"
        verbose_name_plural = "Очки"


class Standing(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='standings', verbose_name="Турнир")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="Игрок")
    points = models.IntegerField("Очки", default=0)
    rank = models.IntegerField("Место", default=0)

    class Meta:
        unique_together = ('tournament', 'player')
        verbose_name = "Турнирная таблица"
        verbose_name_plural = "Турнирные таблицы"


class ClubEvent(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Клуб")
    title = models.CharField("Название события", max_length=200)
    description = models.TextField("Описание", blank=True)
    date = models.DateTimeField("Дата и время проведения")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Создатель")

    class Meta:
        verbose_name = "Событие клуба"
        verbose_name_plural = "События клуба"

    def __str__(self):
        return f"{self.title} ({self.club.name})"


class ClubAdminInvite(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='admin_invites', verbose_name="Клуб")
    email = models.EmailField("Email приглашенного")
    token = models.CharField("Токен", max_length=64, unique=True, editable=False)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Пригласил")
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    accepted_at = models.DateTimeField("Принято", null=True, blank=True)
    is_active = models.BooleanField("Активно", default=True)
    expires_at = models.DateTimeField("Истекает", null=True, blank=True)

    class Meta:
        verbose_name = "Приглашение администратора"
        verbose_name_plural = "Приглашения администраторов"
        indexes = [models.Index(fields=['token'])]

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    def accept(self, user: User):
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            self.is_active = False
            self.save(update_fields=['is_active'])
            return False
        # Email должен совпадать (если у пользователя есть email)
        if user.email and user.email.lower() != self.email.lower():
            return False
        # Создаем связь администратора
        ClubAdmin.objects.get_or_create(user=user, club=self.club)
        # Обеспечиваем членство в клубе
        membership, created = ClubMembership.objects.get_or_create(user=user, club=self.club, defaults={'is_active': True})
        if not membership.is_active:
            membership.is_active = True
            membership.save(update_fields=['is_active'])
        self.accepted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['accepted_at', 'is_active'])
        return True
