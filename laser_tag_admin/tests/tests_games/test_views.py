import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format as date_format
from laser_tag_admin.games.models import Game
from django.contrib.auth.models import User


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='testuser', password='password')


@pytest.fixture
def logged_in_client(client, test_user):
    client.login(username='testuser', password='password')
    return client


@pytest.fixture
def test_game(db):
    return Game.objects.create(
        date=timezone.now().date(),
        start_time=timezone.now().time(),
        location="Test Location"
    )


@pytest.mark.django_db
def test_game_list_view_conditions(logged_in_client, test_game):
    """
    Проверка списка игр при наличии и отсутствии игр.
    """
    url = reverse('game_list')

    # Проверка, если есть игры
    response = logged_in_client.get(url)
    assert response.status_code == 200

    content = response.content.decode('utf-8')
    formatted_date = date_format(test_game.date, 'd.m.Y')

    assert '<table' in content
    assert 'Test Location' in content
    assert formatted_date in content

    # Проверка, если игр нет
    test_game.delete()
    response = logged_in_client.get(url)
    content = response.content.decode('utf-8')
    assert 'Игры не найдены' in content


@pytest.mark.django_db
def test_game_detail_view(logged_in_client, test_game):
    """
    Проверка отображения деталей игры.
    """
    url = reverse('game_detail', args=[test_game.id])
    response = logged_in_client.get(url)

    assert response.status_code == 200

    content = response.content.decode('utf-8')
    formatted_date = date_format(test_game.date, 'd.m.Y')

    assert '<h1>Детали игры</h1>' in content
    assert 'Test Location' in content
    assert formatted_date in content


@pytest.mark.django_db
def test_game_create_view_login_required(client):
    """
    Проверка, что страница создания игры недоступна без авторизации.
    """
    url = reverse('game_create')
    response = client.get(url)
    assert response.status_code == 302  # Redirects to login


@pytest.mark.django_db
def test_game_create_view(logged_in_client):
    """
    Проверка доступа к странице создания игры после авторизации.
    """
    url = reverse('game_create')
    response = logged_in_client.get(url)

    assert response.status_code == 200
    assert '<form' in response.content.decode('utf-8')
