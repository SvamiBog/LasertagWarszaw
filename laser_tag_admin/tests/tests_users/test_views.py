import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_login_view(client):
    url = reverse('login')
    response = client.get(url)

    # Проверка успешного отображения страницы входа
    assert response.status_code == 200, "Страница входа недоступна"
    content = response.content.decode('utf-8')

    # Проверка наличия формы на странице
    assert '<form' in content, "Форма входа не найдена на странице"
    assert '<button type="submit"' in content, "Кнопка отправки формы отсутствует"



@pytest.mark.django_db
def test_logout_view(client):
    # Создаем пользователя и выполняем вход
    user = User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')

    url = reverse('logout')
    response = client.post(url)

    # Проверка перенаправления после выхода
    assert response.status_code == 302  # Проверка на статус кода перенаправления
    assert response.url == reverse('index')

    # Проверка, что пользователь больше не аутентифицирован
    response = client.get(reverse('index'))
    assert '_auth_user_id' not in client.session


@pytest.mark.django_db
def test_user_list_view_login_required(client):
    url = reverse('users_list')
    response = client.get(url)

    # Проверка перенаправления на страницу входа для неаутентифицированных пользователей
    assert response.status_code == 302  # Статус перенаправления
    assert '/login/' in response.url  # Убедимся, что перенаправление идет на страницу входа


@pytest.mark.django_db
def test_user_list_view_authenticated(client):
    # Создаем пользователя и выполняем вход
    user = User.objects.create_user(username='testuser', password='password')
    client.force_login(user)  # Используем force_login для гарантированного входа

    url = reverse('users_list')
    response = client.get(url)

    # Проверка успешного отображения страницы списка пользователей
    assert response.status_code == 200, "Страница списка пользователей недоступна"
    content = response.content.decode('utf-8')

    # Проверка наличия таблицы на странице
    assert '<table' in content, "Таблица отсутствует на странице"
