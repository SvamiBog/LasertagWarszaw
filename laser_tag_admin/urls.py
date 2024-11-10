from django.contrib import admin
from django.urls import path, include
from .views import IndexView, UserLoginView, UserLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('', IndexView.as_view(), name='index'),
    path('users/', include('laser_tag_admin.users.urls')),
    path('games/', include('laser_tag_admin.games.urls')),
]
