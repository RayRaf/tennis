from django import template

register = template.Library()

@register.filter
def tennis_server(score_tuple, first_server=1):
    """
    Определяет, кто должен подавать в настольном теннисе
    Аргументы: score_tuple - кортеж (score1, score2), first_server - кто подает первым (1 или 2)
    Возвращает: 1 если подает первый игрок, 2 если второй
    """
    if isinstance(score_tuple, (list, tuple)) and len(score_tuple) >= 2:
        score1, score2 = int(score_tuple[0]), int(score_tuple[1])
    else:
        return int(first_server) if first_server else 1
    
    total_points = score1 + score2
    first_server = int(first_server) if first_server else 1
    
    # Логика подач в настольном теннисе
    if score1 >= 10 and score2 >= 10:
        # Дейс: по 1 подаче, чередуем каждое очко
        if first_server == 1:
            return 1 if total_points % 2 == 0 else 2
        else:
            return 2 if total_points % 2 == 0 else 1
    else:
        # Обычная игра: по 2 подачи каждого игрока
        serve_group = total_points // 2
        if first_server == 1:
            return 1 if serve_group % 2 == 0 else 2
        else:
            return 2 if serve_group % 2 == 0 else 1

@register.filter 
def is_deuce(score_tuple):
    """
    Проверяет, является ли текущий счет дейсом (10:10 и больше)
    """
    if isinstance(score_tuple, (list, tuple)) and len(score_tuple) >= 2:
        score1, score2 = int(score_tuple[0]), int(score_tuple[1])
        return score1 >= 10 and score2 >= 10
    return False
