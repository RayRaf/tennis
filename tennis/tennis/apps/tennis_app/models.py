from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


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
        friendlies = FriendlyGame.objects.filter(models.Q(player1=self) | models.Q(player2=self))
        match_wins = matches.filter(winner=self).count()
        friendly_wins = friendlies.filter(winner=self).count()
        total_points = Point.objects.filter(scored_by=self).count()
        games = Game.objects.filter(models.Q(match__player1=self) | models.Q(match__player2=self) |
                                     models.Q(friendly__player1=self) | models.Q(friendly__player2=self))
        return {
            'matches': matches.count(),
            'friendlies': friendlies.count(),
            'total_games': matches.count() + friendlies.count(),
            'total_parties': games.count(),
            'wins': match_wins + friendly_wins,
            'losses': (matches.exclude(winner=self).count() + friendlies.exclude(winner=self).count()),
            'scored_points': total_points
        }


class Tournament(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Клуб")
    name = models.CharField("Название турнира", max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Создатель")
    start_date = models.DateField("Дата начала")
    is_round_robin = models.BooleanField("Круговой турнир", default=True)

    class Meta:
        verbose_name = "Турнир"
        verbose_name_plural = "Турниры"

    def __str__(self):
        return self.name


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches', verbose_name="Турнир")
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_as_player1', verbose_name="Игрок 1")
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_as_player2', verbose_name="Игрок 2")
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='wins', verbose_name="Победитель")
    played_at = models.DateTimeField("Дата проведения", auto_now_add=True)

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"

    def __str__(self):
        return f"{self.player1} vs {self.player2} ({self.tournament.name})"


class Game(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='games', verbose_name="Матч", null=True, blank=True)
    friendly = models.ForeignKey('FriendlyGame', on_delete=models.CASCADE, related_name='games', verbose_name="Свободная игра", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    start_time = models.DateTimeField("Начало", null=True, blank=True)
    end_time = models.DateTimeField("Окончание", null=True, blank=True)
    score_player1 = models.PositiveIntegerField("Очки игрока 1", default=0)
    score_player2 = models.PositiveIntegerField("Очки игрока 2", default=0)

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
        self.save()


class FriendlyGame(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name="Клуб")
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='friendlies_as_player1', verbose_name="Игрок 1")
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='friendlies_as_player2', verbose_name="Игрок 2", null=True, blank=True)
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='friendly_wins', verbose_name="Победитель")
    played_at = models.DateTimeField("Дата проведения", auto_now_add=True)

    class Meta:
        verbose_name = "Свободная игра"
        verbose_name_plural = "Свободные игры"

    def __str__(self):
        return f"{self.player1} vs {self.player2 or '—'} (свободная игра)"


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
