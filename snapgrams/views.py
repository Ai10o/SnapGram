from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import PhotoPostForm
from .models import PhotoPost, Comment
from .forms import UserEditForm
from .forms import CommentForm


def home(request):
    posts = PhotoPost.objects.all().order_by('-date_added')
    return render(request, 'snapgrams/home.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PhotoPostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.owner = request.user
            new_post.save()
            return redirect('home')
    else:
        form = PhotoPostForm()
    return render(request, 'snapgrams/upload_photo.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(PhotoPost, id=post_id, owner=request.user)
    if request.method == 'POST':
        form = PhotoPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            if 'delete_image' in request.POST and post.image:
                post.image.delete()
            form.save()
            return redirect('home')
    else:
        form = PhotoPostForm(instance=post)
    return render(request, 'snapgrams/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(PhotoPost, id=post_id, owner=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'snapgrams/delete_post.html', {'post': post})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

def profile(request):
    # Получаем все посты текущего пользователя, упорядоченные по дате
    user_posts = request.user.photopost_set.all().order_by('-date_added')
    # Передаем и пользователя, и его посты в шаблон
    return render(request, 'snapgrams/profile.html', {'user': request.user, 'posts': user_posts})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'registration/edit_profile.html', {'form': form})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(PhotoPost, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        if post.dislikes.filter(id=request.user.id).exists():
            post.dislikes.remove(request.user)
        post.likes.add(request.user)
    return redirect('home')

@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(PhotoPost, id=post_id)
    if post.dislikes.filter(id=request.user.id).exists():
        post.dislikes.remove(request.user)
    else:
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        post.dislikes.add(request.user)
    return redirect('home')


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(PhotoPost, id=post_id)
    comments = post.comments.all()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()
    return render(request, 'snapgrams/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    if comment.author == request.user:
        comment.delete()
    return redirect('post_detail', post_id=post_id)
