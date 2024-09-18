from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from .forms import SignUpForm, LoginForm, PostForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Post, Comment
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import render


def home(request):
    posts = Post.objects.all().order_by("-timestamp")
    return render(request, "blog/home.html", {"posts": posts})


def about(request):
    return render(request, "blog/about.html")


def contact(request):
    return render(request, "blog/contact.html")


def dashboard(request):
    if request.user.is_authenticated:
        posts = Post.objects.all()
        user = request.user
        full_name = user.get_full_name()
        groups = user.groups.all()
        return render(
            request,
            "blog/dashboard.html",
            {"posts": posts, "full_name": full_name, "groups": groups},
        )
    else:
        return HttpResponseRedirect("/login/")


def user_signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulation !! You have become an author")
            user = form.save()
            group = Group.objects.get(name="Author")
            user.groups.add(group)
            return HttpResponseRedirect("/")
    else:
        form = SignUpForm()
    return render(request, "blog/signup.html", {"form": form})


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = LoginForm(request=request, data=request.POST)
            if form.is_valid():
                user_name = form.cleaned_data["username"]
                user_password = form.cleaned_data["password"]
                user = authenticate(username=user_name, password=user_password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "LoggedIn successfully")
                    return HttpResponseRedirect("/dashboard/")
        else:
            form = LoginForm()
        return render(request, "blog/login.html", {"form": form})
    else:
        return HttpResponseRedirect("/dashboard/")


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/")


def add_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data["title"]
                description = form.cleaned_data["description"]
                timestamp = form.cleaned_data["timestamp"]
                status = form.cleaned_data["status"]
                post = Post(
                    title=title,
                    description=description,
                    timestamp=timestamp,
                    status=status,
                )
                post.save()
                # form = PostForm()

                # Broadcast the new post to the WebSocket group
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "blog_updates",
                    {
                        "type": "blog_post_update",  # Ensure this matches the consumer's method name
                        "data": {
                            "id": post.id,
                            "title": post.title,
                            "description": post.description,
                            "timestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "status": post.status,
                        },
                    },
                )

                return HttpResponseRedirect("/")
        else:
            form = PostForm()
        return render(request, "blog/addpost.html", {"form": form})
    else:
        return HttpResponseRedirect("/login/")


def update_post(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            post = Post.objects.get(pk=id)
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                # messages.success(request, 'Data updated')
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "blog_updates",
                    {
                        "type": "blog_post_edit",  # Ensure this matches the consumer's method name
                        "data": {
                            "id": post.id,
                            "title": post.title,
                            "description": post.description,
                            "timestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "status": post.status,
                        },
                    },
                )
                return HttpResponseRedirect("/dashboard/")
        else:
            post = Post.objects.get(pk=id)
            form = PostForm(instance=post)
        return render(request, "blog/updatepost.html", {"form": form})
    else:
        return HttpResponseRedirect("/login/")


def delete_post(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            post = Post.objects.get(pk=id)
            post.delete()
            # Broadcast the delete post to the WebSocket group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "blog_updates",  # Use the same group name as in the consumer
                {
                    "type": "blog_delete_post",  # Ensure this matches the consumer's method name
                    "data": {
                        "id": id,  # Include the post ID for reference
                    },
                },
            )

            return HttpResponseRedirect("/dashboard/")
    else:
        return HttpResponseRedirect("/login/")


@login_required
@require_POST
def add_comment(request):
    # Get data from POST request
    data = json.loads(request.body)
    post_id = data.get("post_id")
    content = data.get("content")

    # Validate input
    if not post_id or not content:
        return JsonResponse({"error": "Invalid input"}, status=400)

    # Save comment to the database
    post = Post.objects.get(id=post_id)
    comment = Comment(post=post, user=request.user, content=content)
    comment.save()

    # Broadcast comment to WebSocket group
    channel_layer = get_channel_layer()

    # Debugging print
    print(
        "resonse is:",
        {
            "post_id": post_id,
            "user": request.user.username,
            "content": content,
            "timestamp": comment.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    async_to_sync(channel_layer.group_send)(
        "blog_updates",
        {
            "type": "new_comment",
            "data": {
                "post_id": post_id,
                "user": request.user.username,
                "content": content,
                "timestamp": comment.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),  # Assuming Comment model has timestamp
            },
        },
    )

    return JsonResponse({"message": "Comment added successfully"})



def get_comments(request, post_id):
    comments = Comment.objects.filter(post_id=post_id).order_by("-timestamp")
    comments_data = [
        {
            "user": comment.user.username,
            "content": comment.content,
            "timestamp": comment.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for comment in comments
    ]
    return JsonResponse({"comments": comments_data})
