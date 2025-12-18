from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileForm

User = get_user_model()


def get_paginated_page(queryset, request, per_page=10):
    """
    Создает пагинатор и возвращает запрошенную страницу. 
    Args:
        queryset: QuerySet с объектами для пагинации
        request: HttpRequest объект для получения номера страницы
        per_page: количество объектов на странице (по умолчанию 10)
    Returns:
        Page object с объектами для текущей страницы
    """

    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """
    Главная страница с последними публикациями.
    Показывает только опубликованные посты с не истекшей датой публикации.
    Использует пагинацию по 10 постов на страницу.
    Returns:
        Страницу с шаблоном blog/index.html с постами
    """

    posts = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).select_related('author', 'category', 'location').prefetch_related(
        'comments').order_by('-pub_date')
    page_obj = get_paginated_page(posts, request)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    """
    Отображает полный текст поста и комментарии к нему.
    Автор видит все свои посты, включая отложенные и снятые с публикации.
    Остальные пользователи видят только опубликованные посты.
    Args:
        request: HttpRequest объект
        id: ID поста для отображения
    Returns:
        Использует функцию render() для создания HTML с шаблоном
        blog/detail.html с выводом поста и комментариями"
    """

    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location')
        .prefetch_related('comments__author'),
        id=id
    )
    can_view = (
        post.is_published and post.pub_date <= timezone.now()
        and post.category.is_published
    )
    if request.user != post.author and not can_view:
        return render(request, 'pages/404.html', status=404)
    form = CommentForm()
    comments = post.comments.all()
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
        'comments': comments
    })


def category_posts(request, category_slug):
    """
    Отображает все посты определенной категории.
    Args:
        request: HttpRequest объект
        category_slug: slug категории для фильтрации постов
    Returns:
        Рендерит шаблон blog/category.html с постами категории
    """

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('author', 'location').prefetch_related(
        'comments'
    ).order_by('-pub_date')
    page_obj = get_paginated_page(posts, request)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })


@login_required
def create_post(request):
    """
    Создает новую публикацию.
    Доступно только авторизованным пользователям.
    Поддерживает отложенную публикацию через поле pub_date.
    Args:
        request: HttpRequest объект
    Returns:
        Рендерит форму создания поста
    """

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.pub_date > timezone.now():
                post.is_published = True
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, id):
    """
    Редактирует существующую публикацию.
    Доступно только автору публикации.
    Остальные пользователи перенаправляются на страницу поста.
    Args:
        request: HttpRequest объект
        id: ID поста для редактирования
    Returns:
        Открывает форму редактирования или перенаправляет на пост
    """

    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, id):
    """
    Удаляет публикацию после подтверждения.
    Доступно только автору публикации.
    GET-запрос показывает страницу подтверждения,
    POST-запрос выполняет удаление.
    Args:
        request: HttpRequest объект
        id: ID поста для удаления
    Returns:
        Страница подтверждения
    """

    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        # Если пользователь подтвердил удаление
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    # Если GET-запрос, то показываем подтверждение
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {
        'form': form,
        'post': post,
    })


@login_required
def add_comment(request, id):
    """
    Добавляет комментарий к посту.
    Доступно только авторизованным пользователям.
    Args:
        request: HttpRequest объект
        id: ID поста для комментирования
    Returns:
        Перенаправляет на страницу поста
    """

    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)  # Не сохраняем сразу
            comment.post = post  # Привязываем к посту
            comment.author = request.user  # Устанавливаем автора
            comment.save()  # Теперь сохраняем
    return redirect('blog:post_detail', id=id)


@login_required
def edit_comment(request, id, comment_id):
    """
    Редактирует существующий комментарий.
    Доступно только автору комментария.
    Args:
        request: HttpRequest объект
        id: ID поста
        comment_id: ID комментария для редактирования
    Returns:
        Форма редактирования
    """

    comment = get_object_or_404(Comment, id=comment_id, post_id=id)
    if comment.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html', {
        'comment': comment,
        'form': form,
    })


@login_required
def delete_comment(request, id, comment_id):
    """
    Удаляет комментарий после подтверждения.
    Доступно только автору комментария.
    GET-запрос показывает страницу подтверждения,
    POST-запрос выполняет удаление.
    Args:
        request: HttpRequest объект
        id: ID поста
        comment_id: ID комментария для удаления
    Returns:
        Страница подтверждения
    """

    comment = get_object_or_404(Comment, id=comment_id, post_id=id)
    if comment.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=id)
    form = CommentForm(
        instance=comment) if '/edit_comment/' in request.path else None
    return render(request, 'blog/comment.html', {
        'comment': comment,
        'form': form,
    })


def profile(request, username):
    """
    Отображает профиль пользователя и его публикации.
    Автор видит все свои посты, включая отложенные.
    Остальные пользователи видят только опубликованные посты.
    Args:
        request: HttpRequest объект
        username: Имя пользователя для отображения профиля
    Returns:
        Рендерит шаблон blog/profile.html с данными пользователя
    """

    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        posts = profile_user.posts.all()
    else:
        posts = profile_user.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )
    posts = posts.select_related('category', 'location').prefetch_related(
        'comments'
    ).order_by('-pub_date')
    page_obj = get_paginated_page(posts, request)
    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj
    })


@login_required
def edit_profile(request):
    """
    Редактирует профиль текущего пользователя.
    Позволяет изменить имя пользователя, email, имя и фамилию.
    Не включает изменение пароля (отдельная страница).
    Args:
        request: HttpRequest объект
    Returns:
        Форма редактирования профиля
    """

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})
