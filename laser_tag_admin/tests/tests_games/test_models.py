import pytest
from django.utils import timezone
from laser_tag_admin.games.models import Game, GameRegistration
from laser_tag_admin.users.models import User
import pytz

@pytest.mark.django_db
def test_game_str_representation():
    game = Game.objects.create(
        date=timezone.now().date(),
        start_time=timezone.now().time(),
        location="Test Location"
    )
    assert str(game) == f"Игра {game.id} - {game.date} {game.start_time}"


@pytest.mark.django_db
def test_game_get_total_players_count():
    game = Game.objects.create(
        date=timezone.now().date(),
        start_time=timezone.now().time(),
        location="Test Location"
    )
    # Создание пользователя с telegram_id
    user = User.objects.create(
        telegram_id=12345,  # Пример значения для telegram_id
        username="testuser",
        first_name="John",
        last_name="Doe"
    )

    GameRegistration.objects.create(
        user=user,
        game=game,
        guests_count=2
    )

    assert game.get_total_players_count() == 3


@pytest.mark.django_db
def test_game_get_status_display():
    warsaw_timezone = pytz.timezone('Europe/Warsaw')
    current_datetime = timezone.now().astimezone(warsaw_timezone)

    # Создаем игру, которая еще не началась
    upcoming_game = Game.objects.create(
        date=(current_datetime + timezone.timedelta(days=1)).date(),
        start_time=(current_datetime + timezone.timedelta(days=1)).time(),
        location="Upcoming Location"
    )
    assert upcoming_game.get_status_display() == 'Предстоящая игра'

    # Создаем игру, которая проходит сейчас
    ongoing_game = Game.objects.create(
        date=current_datetime.date(),
        start_time=current_datetime.time(),
        location="Ongoing Location"
    )
    assert ongoing_game.get_status_display() == 'Проходит сейчас'

    # Создаем игру, которая уже закончилась
    completed_game = Game.objects.create(
        date=(current_datetime - timezone.timedelta(days=1)).date(),
        start_time=(current_datetime - timezone.timedelta(days=1)).time(),
        location="Completed Location"
    )
    assert completed_game.get_status_display() == 'Закончена'


@pytest.mark.django_db
def test_game_registration_str_representation():
    user = User.objects.create(
        telegram_id=12345,  # Пример значения
        username="testuser",
        first_name="John",
        last_name="Doe"
    )
    game = Game.objects.create(
        date=timezone.now().date(),
        start_time=timezone.now().time(),
        location="Test Location"
    )
    registration = GameRegistration.objects.create(
        user=user,
        game=game,
        guests_count=1
    )

    assert str(registration) == f"{user} - Игра {game.id} (1 гостей)"
