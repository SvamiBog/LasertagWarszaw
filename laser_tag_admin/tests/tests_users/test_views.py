import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_login_view(client):
    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in str(response.content)

@pytest.mark.django_db
def test_logout_view(client):
    user = User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')
    url = reverse('logout')
    response = client.post(url)
    assert response.status_code == 302  # Redirect status code
    assert response.url == reverse('index')

@pytest.mark.django_db
def test_user_list_view_login_required(client):
    url = reverse('users_list')
    response = client.get(url)
    assert response.status_code == 302  # Redirects to login if not authenticated
