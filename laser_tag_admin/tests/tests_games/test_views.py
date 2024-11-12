import pytest
from django.urls import reverse
from laser_tag_admin.games.models import Game
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.dateformat import format as date_format

@pytest.mark.django_db
def test_game_list_view(client):
    # Создаем пользователя и выполняем вход
    user = User.objects.create(username='testuser')
    client.force_login(user)

    # Создаем тестовую игру
    game = Game.objects.create(
        date=timezone.now().date(),
        start_time=timezone.now().time(),
        location="Test Location"
    )

    url = reverse('game_list')
    response = client.get(url)

    # Проверяем статус ответа
    assert response.status_code == 200

    # Проверяем, что на странице присутствует таблица с играми и детали игры
    content = response.content.decode('utf-8')

    # Приведи дату к формату d.m.Y
    formatted_date = date_format(game.date, 'd.m.Y')
    assert '<table' in content
    assert 'Test Location' in content
    assert formatted_date in content


@pytest.mark.django_db
def test_game_detail_view(client):
    # Создаем пользователя и выполняем вход
    user = User.objects.create(username='testuser')
    client.force_login(user)

    # Создаем тестовую игру
    game = Game.objects.create(
        date=timezone.now().date(),
        start_time=timezone.now().time(),
        location="Test Location"
    )

    url = reverse('game_detail', args=[game.id])
    response = client.get(url)

    # Проверяем статус ответа
    assert response.status_code == 200

    # Преобразуем содержимое в строку с правильной кодировкой
    content = response.content.decode('utf-8')

    # Приведи дату к формату d.m.Y
    formatted_date = date_format(game.date, 'd.m.Y')
    assert '<h1>Детали игры</h1>' in content
    assert 'Test Location' in content
    assert formatted_date in content


@pytest.mark.django_db
def test_game_create_view_login_required(client):
    url = reverse('game_create')
    response = client.get(url)
    assert response.status_code == 302  # Redirects to login if not authenticated

@pytest.mark.django_db
def test_game_create_view(client):
    # Создаем пользователя и выполняем вход
    user = User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')

    url = reverse('game_create')
    response = client.get(url)

    # Проверяем доступ к странице создания игры
    assert response.status_code == 200
    assert '<form' in response.content.decode('utf-8')

@pytest.mark.django_db
def test_game_list_no_games(client):
    # Создаем пользователя и выполняем вход
    user = User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')

    url = reverse('game_list')
    response = client.get(url)

    # Проверяем, что сообщение об отсутствии игр отображается
    content = response.content.decode('utf-8')
    assert 'Игры не найдены' in content
