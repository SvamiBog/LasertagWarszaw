from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import User
from .forms import UserForm

class UserIndexView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/users_list.html'  # Путь к шаблону
    context_object_name = 'users'  # Имя переменной контекста для списка пользователей


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'users/user_edit.html'
    context_object_name = 'user'

    def get_success_url(self):
        return reverse_lazy('users_list')

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    context_object_name = 'user'
    success_url = reverse_lazy('users_list')  # Перенаправление после успешного удаления
