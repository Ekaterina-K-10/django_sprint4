from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileForm

User = get_user_model()


# Отображает список последних публикаций с пагинацией
def index(request):
    posts = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).select_related('author', 'category', 'location').prefetch_related(
        'comments'
    ).order_by('-pub_date')  # Сортировка от новых к старым
    # Пагинация: разбиваем на страницы по 10 постов
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


# Отображает полный текст поста и комментарии к нему
def post_detail(request, id):
    try:
        post = Post.objects.select_related('author', 'category', 'location').prefetch_related(
            'comments__author'
        ).get(id=id)

        # Проверяем, может ли пользователь видеть пост
        can_view = (
            post.is_published
            and post.pub_date <= timezone.now()
            and post.category.is_published
        )

        # Автор может видеть свой пост в любом случае
        if request.user != post.author and not can_view:
            raise Http404

    except Post.DoesNotExist:
        raise Http404

    form = CommentForm()
    comments = post.comments.all()

    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
        'comments': comments
    })


# Отображает все посты определенной категории
def category_posts(request, category_slug):
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

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Если пост отложенный, не делаем его опубликованным автоматически
            if post.pub_date > timezone.now():
                post.is_published = True  # Но автор должен видеть его

            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, id):
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
    post = get_object_or_404(Post, id=id)

    if post.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    # Создаем форму с instance поста для шаблона
    form = PostForm(instance=post)

    return render(request, 'blog/create.html', {
        'form': form,
        'post': post,
    })


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

    return redirect('blog:post_detail', id=id)


@login_required
def edit_comment(request, id, comment_id):
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
    comment = get_object_or_404(Comment, id=comment_id, post_id=id)

    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=id)

    # Для GET-запроса показываем шаблон comment.html с контекстом удаления
    form = CommentForm(
        instance=comment) if '/edit_comment/' in request.path else None

    return render(request, 'blog/comment.html', {
        'comment': comment,
        'form': form,
    })


# Отображение профиля пользователя и его публикаций
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Для автора показываем все посты
    if request.user == profile_user:
        posts = profile_user.posts.all()
    else:
        # Для других - только опубликованные и не отложенные
        posts = profile_user.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )

    posts = posts.select_related('category', 'location').prefetch_related(
        'comments'
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj
    })


# Форма для изменения данных пользователя
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})
