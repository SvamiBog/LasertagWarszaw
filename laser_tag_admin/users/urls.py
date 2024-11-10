from django.urls import path
from .views import UserIndexView, UserUpdateView, UserDeleteView


urlpatterns = [
    path('', UserIndexView.as_view(), name='users_list'),
    path('edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
]
