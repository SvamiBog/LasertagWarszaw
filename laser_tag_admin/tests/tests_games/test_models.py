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
    expected_str = f"Игра {game.id} - {game.date} {game.start_time}"
    assert str(game) == expected_str, f"Expected {expected_str}, but got {str(game)}"


@pytest.mark.django_db
def test_game_get_total_players_count():
    game = Game.objects.create(
        date=timezone.now().date(),
        start_time=timezone.now().time(),
        location="Test Location"
    )
    user = User.objects.create(
        telegram_id=12345,
        username="testuser",
        first_name="John",
        last_name="Doe"
    )

    GameRegistration.objects.create(
        user=user,
        game=game,
        guests_count=2
    )

    total_players = game.get_total_players_count()
    assert total_players == 3, f"Expected total players to be 3, but got {total_players}"


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
    assert upcoming_game.get_status_display() == 'Предстоящая игра', "Expected status to be 'Предстоящая игра'"

    # Создаем игру, которая проходит сейчас
    ongoing_game = Game.objects.create(
        date=current_datetime.date(),
        start_time=(current_datetime - timezone.timedelta(hours=1)).time(),
        location="Ongoing Location"
    )
    assert ongoing_game.get_status_display() == 'Проходит сейчас', "Expected status to be 'Проходит сейчас'"

    # Создаем игру, которая уже закончилась
    completed_game = Game.objects.create(
        date=(current_datetime - timezone.timedelta(days=1)).date(),
        start_time=(current_datetime - timezone.timedelta(days=1)).time(),
        location="Completed Location"
    )
    assert completed_game.get_status_display() == 'Закончена', "Expected status to be 'Закончена'"


@pytest.mark.django_db
def test_game_registration_str_representation():
    user = User.objects.create(
        telegram_id=12345,
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

    expected_str = f"{user} - Игра {game.id} (1 гостей)"
    assert str(registration) == expected_str, f"Expected {expected_str}, but got {str(registration)}"
