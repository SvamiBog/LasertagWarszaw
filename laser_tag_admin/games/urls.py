from django.urls import path
from .views import GameListView, GameDetailView, GameUpdateView, GameDeleteView, GameCreateView

urlpatterns = [
    path('', GameListView.as_view(), name='game_list'),
    path('<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('<int:pk>/edit/', GameUpdateView.as_view(), name='game_edit'),
    path('<int:pk>/delete/', GameDeleteView.as_view(), name='game_delete'),
    path('create/', GameCreateView.as_view(), name='game_create'),
]
