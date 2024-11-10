from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from .models import Game
from django.contrib.auth.mixins import LoginRequiredMixin


class GameListView(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'games/game_list.html'
    context_object_name = 'games'

    def get_queryset(self):
        games = Game.objects.all()
        for game in games:
            game.status_display = game.get_status_display()
        return games

class GameDetailView(LoginRequiredMixin, DetailView):
    model = Game
    template_name = 'games/game_detail.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.object.get_status_display()
        return context


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    template_name = 'games/game_form.html'
    fields = ['date', 'start_time', 'location']
    success_url = reverse_lazy('game_list')


class GameUpdateView(LoginRequiredMixin, UpdateView):
    model = Game
    template_name = 'games/game_edit.html'
    fields = ['date', 'start_time', 'location']
    context_object_name = 'game'

    def get_success_url(self):
        return reverse_lazy('game_list')


class GameDeleteView(LoginRequiredMixin, DeleteView):
    model = Game
    template_name = 'games/game_confirm_delete.html'
    context_object_name = 'game'
    success_url = reverse_lazy('game_list')
