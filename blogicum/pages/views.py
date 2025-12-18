from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from blog.forms import RegistrationForm
from django.views.generic import TemplateView

User = get_user_model()


class AboutView(TemplateView):
    """
    View-класс для страницы 'О проекте'.
    Attributes:
        template_name: Путь к шаблону страницы
    """

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """
    View-класс для страницы 'Правила сайта'.
    Attributes:
        template_name: Путь к шаблону страницы
    """
  
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """
    Обработчик кастомной страницы ошибки 404.
    Args:
        request: HttpRequest объект
        exception: Исключение, вызвавшее ошибку 404
    Returns:
        Рендерит страницу 404
    """

    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """
    Обработчик кастомной страницы ошибки 500.
    Args:
        request: HttpRequest объект
    Returns:
        Рендерит страницу 500
    """

    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """
    Обработчик кастомной страницы ошибки CSRF 403.
    Args:
        request: HttpRequest объект
        reason: Причина ошибки CSRF
    Returns:
        Рендерит страницу 403
    """

    return render(request, 'pages/403csrf.html', status=403)


class PageCreateView(LoginRequiredMixin, CreateView):
    """
    View-класс для создания статичных страниц.
    Доступно только авторизованным пользователям.
    Attributes:
        template_name: Путь к шаблону формы
        fields: Поля для создания страницы
        success_url: URL для перенаправления после успешного создания
    """

    template_name = 'pages/create.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('pages:about')
    
    def form_valid(self, form):
        """
        Добавляет автора к создаваемой странице.
        Args:
            form: Валидная форма
        Returns:
            Результат родительского метода form_valid
        """

        form.instance.author = self.request.user
        return super().form_valid(form)


class PageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View-класс для редактирования статичных страниц.
    Доступно только администраторам.
    Attributes:
        template_name: Путь к шаблону формы
        fields: Поля для редактирования
        success_url: URL для перенаправления после успешного редактирования
    """

    template_name = 'pages/edit.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('pages:about')
    
    def test_func(self):
        """
        Проверяет, является ли пользователь администратором.
        Returns:
            bool: True если пользователь администратор, иначе False
        """
        return self.request.user.is_staff


class PageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View-класс для удаления статичных страниц.
    Доступно только администраторам.
    Attributes:
        template_name: Путь к шаблону подтверждения удаления
        success_url: URL для перенаправления после успешного удаления
    """
    
    template_name = 'pages/delete.html'
    success_url = reverse_lazy('pages:about')
    
    def test_func(self):
        """
        Проверяет, является ли пользователь администратором.
        Returns:
            bool: True если пользователь администратор, иначе False
        """

        return self.request.user.is_staff


class RegistrationView(CreateView):
    """
    View-класс для регистрации новых пользователей.
    Attributes:
        form_class: Класс формы для регистрации
        template_name: Путь к шаблону формы регистрации
        success_url: URL для перенаправления после успешной регистрации
    """
    
    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
