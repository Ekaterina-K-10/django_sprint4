from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Category, Location

User = get_user_model()


class PostForm(forms.ModelForm):
    """
    Форма для создания и редактирования публикаций.
    Fields:
        title: Заголовок поста
        text: Текст поста
        pub_date: Дата и время публикации
        image: Изображение к посту
        category: Категория поста
        location: Местоположение
    """

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_published=True),
        label='Категория',
        empty_label=None
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_published=True),
        label='Местоположение',
        required=False,
        empty_label='Не выбрано'
    )

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'image', 'category', 'location')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        help_texts = {
            'pub_date': (
                'Если установить дату и время в будущем — '
                'можно делать отложенные публикации.'
            ),
        }


class CommentForm(forms.ModelForm):
    """
    Форма для добавления и редактирования комментариев.
    Fields:
        text: Текст комментария
    """

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


class RegistrationForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.
    Fields:
        username: Имя пользователя
        email: Email адрес
        first_name: Имя
        last_name: Фамилия
        password1: Пароль
        password2: Подтверждение пароля
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'password1', 'password2')


class ProfileForm(forms.ModelForm):
    """
    Форма редактирования профиля пользователя.
    Fields:
        username: Имя пользователя
        email: Email адрес
        first_name: Имя
        last_name: Фамилия
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={'required': True}),
        }
