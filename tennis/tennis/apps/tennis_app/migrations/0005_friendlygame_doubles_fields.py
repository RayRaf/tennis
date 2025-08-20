from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('tennis_app', '0004_game_first_server'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendlygame',
            name='game_type',
            field=models.CharField(choices=[('single', 'Одиночная'), ('double', 'Парная')], default='single', max_length=10, verbose_name='Тип игры'),
        ),
        migrations.AddField(
            model_name='friendlygame',
            name='team1_player1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doubles_team1_p1', to='tennis_app.player', verbose_name='Команда 1 Игрок 1'),
        ),
        migrations.AddField(
            model_name='friendlygame',
            name='team1_player2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doubles_team1_p2', to='tennis_app.player', verbose_name='Команда 1 Игрок 2'),
        ),
        migrations.AddField(
            model_name='friendlygame',
            name='team2_player1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doubles_team2_p1', to='tennis_app.player', verbose_name='Команда 2 Игрок 1'),
        ),
        migrations.AddField(
            model_name='friendlygame',
            name='team2_player2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doubles_team2_p2', to='tennis_app.player', verbose_name='Команда 2 Игрок 2'),
        ),
        migrations.AddField(
            model_name='friendlygame',
            name='winning_team',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Команда 1'), (2, 'Команда 2')], null=True, verbose_name='Победившая команда'),
        ),
    ]
