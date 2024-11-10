import pytest
from django.urls import reverse
from laser_tag_admin.games.models import Game
from django.utils import timezone
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_game_list_view(client):
    # Создаем пользователя и выполняем вход
    user = User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')

    # Создаем тестовую игру для проверки отображения
    Game.objects.create(
        date=timezone.now().date(),
        start_time=timezone.now().time(),
        location="Test Location"
    )

    url = reverse('game_list')
    response = client.get(url)

    # Проверяем статус ответа
    assert response.status_code == 200

    # Проверяем, что на странице присутствует таблица с играми
    assert '<table' in str(response.content)
    assert 'Test Location' in str(response.content)


@pytest.mark.django_db
def test_game_detail_view(client):
    # Создаем пользователя и выполняем вход
    user = User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')

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

    # Проверяем наличие информации об игре на странице
    assert game.location in content
    assert '<h1>Детали игры</h1>' in content


@pytest.mark.django_db
def test_game_create_view_login_required(client):
    url = reverse('game_create')
    response = client.get(url)
    assert response.status_code == 302  # Redirects to login if not authenticated
