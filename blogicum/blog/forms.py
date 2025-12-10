from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Category, Location

User = get_user_model()


# Форма для добавления или изменения публикации
class PostForm(forms.ModelForm):
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


# Форма для создания и изменения комментариев к постам
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


# Форма для создания нового аккаунта пользователя
class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'password1', 'password2')


# Форма для изменения данных пользователя
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={'required': True}),
        }
