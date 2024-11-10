from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = '/login/'  # Путь для перенаправления на страницу входа
    redirect_field_name = 'redirect_to'

    extra_context = {
        'title': _('Welcome to the Bot Administration Panel!'),
        'text': _('Manage your bot users and settings easily.'),
        'button_text': _('View Users')
    }


class UserLoginView(LoginView):
    template_name = 'form.html'
    authentication_form = AuthenticationForm
    next_page = reverse_lazy('index')
    extra_context = {
        'title': _('Authorization'),
        'button_text': _('Login')
    }
    success_message = _('You are Logged in')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.INFO, _('You are logged out'))
        return HttpResponseRedirect(self.next_page)
