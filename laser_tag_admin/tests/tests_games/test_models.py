import pytest
from laser_tag_admin.games.models import Game
from django.utils import timezone
import pytz

@pytest.mark.django_db
def test_game_status_upcoming():
    warsaw_timezone = pytz.timezone('Europe/Warsaw')
    current_datetime = timezone.now().astimezone(warsaw_timezone)
    game = Game.objects.create(
        date=current_datetime.date(),
        start_time=(current_datetime + timezone.timedelta(hours=3)).time(),
        location="Test Location"
    )

    game_datetime = timezone.make_aware(timezone.datetime.combine(game.date, game.start_time), warsaw_timezone)
    assert current_datetime < game_datetime

@pytest.mark.django_db
def test_game_status_ongoing():
    warsaw_timezone = pytz.timezone('Europe/Warsaw')
    current_datetime = timezone.now().astimezone(warsaw_timezone)
    game = Game.objects.create(
        date=current_datetime.date(),
        start_time=current_datetime.time(),
        location="Test Location"
    )
    game_datetime = timezone.make_aware(timezone.datetime.combine(game.date, game.start_time), warsaw_timezone)
    end_datetime = game_datetime + timezone.timedelta(hours=2)
    assert game_datetime <= current_datetime <= end_datetime

@pytest.mark.django_db
def test_game_status_completed():
    warsaw_timezone = pytz.timezone('Europe/Warsaw')
    current_datetime = timezone.now().astimezone(warsaw_timezone)
    game = Game.objects.create(
        date=(current_datetime - timezone.timedelta(days=1)).date(),
        start_time=(current_datetime - timezone.timedelta(hours=3)).time(),
        location="Test Location"
    )
    game_datetime = timezone.make_aware(timezone.datetime.combine(game.date, game.start_time), warsaw_timezone)
    end_datetime = game_datetime + timezone.timedelta(hours=2)
    assert current_datetime > end_datetime
