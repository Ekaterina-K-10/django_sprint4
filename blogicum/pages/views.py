from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from blog.forms import RegistrationForm
# Используем CBV для статичных страниц
from django.views.generic import TemplateView

User = get_user_model()


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Страница 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Страница 500."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """Страница 403 CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


# CBV для статичных страниц
class PageCreateView(LoginRequiredMixin, CreateView):
    template_name = 'pages/create.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('pages:about')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'pages/edit.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('pages:about')
    
    def test_func(self):
        return self.request.user.is_staff


class PageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'pages/delete.html'
    success_url = reverse_lazy('pages:about')
    
    def test_func(self):
        return self.request.user.is_staff


# Регистрация пользователя
class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
