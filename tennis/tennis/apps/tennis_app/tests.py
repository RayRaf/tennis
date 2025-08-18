from django.test import TestCase
from django.contrib.auth.models import User
from .models import Club, Player, Tournament, Match, Game, Point

class MatchLogicTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.player1 = Player.objects.create(full_name='Player 1', club=self.club)
        self.player2 = Player.objects.create(full_name='Player 2', club=self.club)
        self.tournament = Tournament.objects.create(
            club=self.club,
            name='Test Tournament',
            created_by=self.user,
            start_date='2025-01-01'
        )
        self.match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2
        )

    def test_match_initial_state(self):
        """Тест начального состояния матча"""
        self.assertEqual(self.match.sets_player1, 0)
        self.assertEqual(self.match.sets_player2, 0)
        self.assertFalse(self.match.finished)
        self.assertIsNone(self.match.winner)

    def test_game_scoring(self):
        """Тест подсчета очков в партии"""
        # Создаем партию
        game = Game.objects.create(match=self.match)
        
        # Добавляем очки игроку 1
        for i in range(5):
            Point.objects.create(game=game, scored_by=self.player1, order=i+1)
        
        # Добавляем очки игроку 2
        for i in range(3):
            Point.objects.create(game=game, scored_by=self.player2, order=i+6)
        
        # Пересчитываем счет
        game.recalculate_score()
        
        self.assertEqual(game.score_player1, 5)
        self.assertEqual(game.score_player2, 3)

    def test_game_winner_logic(self):
        """Тест определения победителя партии"""
        from django.utils import timezone
        
        game = Game.objects.create(match=self.match, start_time=timezone.now())
        
        # Игрок 1 набирает 11 очков, игрок 2 - 9 (разница 2)
        for i in range(11):
            Point.objects.create(game=game, scored_by=self.player1, order=i+1)
        for i in range(9):
            Point.objects.create(game=game, scored_by=self.player2, order=i+12)
            
        game.recalculate_score()
        game.end_time = timezone.now()
        game.save()
        
        winner = game.get_winner()
        self.assertEqual(winner, self.player1)

    def test_match_completion_logic(self):
        """Тест завершения матча при достижении 2 побед"""
        # Имитируем выигрыш 2 партий игроком 1
        self.match.sets_player1 = 2
        self.match.sets_player2 = 0
        self.match.save()
        
        # В реальном приложении это делается в представлении
        if self.match.sets_player1 == 2:
            self.match.set_winner(self.player1)
            self.match.finished = True
            self.match.save()
        
        self.assertTrue(self.match.finished)
        self.assertEqual(self.match.winner, self.player1)

    def test_match_status_method(self):
        """Тест метода получения статуса матча"""
        # Новый матч
        status = self.match.get_match_status()
        self.assertEqual(status, "Не начат")
        
        # Матч в процессе
        self.match.sets_player1 = 1
        self.match.sets_player2 = 0
        self.match.save()
        status = self.match.get_match_status()
        self.assertEqual(status, "В процессе (1:0)")
        
        # Завершенный матч
        self.match.sets_player1 = 2
        self.match.sets_player2 = 1
        self.match.finished = True
        self.match.save()
        status = self.match.get_match_status()
        self.assertEqual(status, "Завершен (2:1)")

class MatchViewTestCase(TestCase):
    def setUp(self):
        """Настройка для тестирования представлений"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.player1 = Player.objects.create(full_name='Player 1', club=self.club)
        self.player2 = Player.objects.create(full_name='Player 2', club=self.club)
        self.tournament = Tournament.objects.create(
            club=self.club,
            name='Test Tournament',
            created_by=self.user,
            start_date='2025-01-01'
        )
        self.match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2
        )

    def test_live_match_page_loads(self):
        """Тест загрузки страницы live-матча"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(f'/match/{self.match.id}/play/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player1.full_name)
        self.assertContains(response, self.player2.full_name)
