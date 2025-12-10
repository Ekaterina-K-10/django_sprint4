from django.urls import path
from . import views
from .views import RegistrationView

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('rules/', views.RulesView.as_view(), name='rules'),
    # Регистрация
    path('auth/registration/', RegistrationView.as_view(),
         name='registration'),
    # CBV для статичных страниц
    path('create/', views.PageCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.PageUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.PageDeleteView.as_view(), name='delete'),
]
