from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import UserProfile


def register(request):
    if request.user.is_authenticated:
        return redirect('progress:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        display_name = request.POST.get('display_name', '').strip()
        grade_level = request.POST.get('grade_level', '9')
        theme = request.POST.get('theme', 'midnight')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            if display_name:
                user.first_name = display_name
                user.save()
            UserProfile.objects.create(
                user=user,
                theme=theme,
                grade_level=grade_level,
                display_name=display_name,
            )
            login(request, user)
            messages.success(request, f'Welcome to Libria, {user.first_name or username}! 🎓')
            return redirect('progress:dashboard')
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('progress:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'progress:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('core:landing')


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile_obj.display_name = request.POST.get('display_name', '').strip()
        profile_obj.theme = request.POST.get('theme', 'midnight')
        profile_obj.grade_level = request.POST.get('grade_level', '9')
        profile_obj.ai_provider = request.POST.get('ai_provider', 'gemini')
        profile_obj.ai_api_key = request.POST.get('ai_api_key', '').strip()
        profile_obj.study_goal_minutes = int(request.POST.get('study_goal_minutes', 120))
        if 'avatar' in request.FILES:
            profile_obj.avatar = request.FILES['avatar']
        profile_obj.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'profile': profile_obj})


@login_required
def set_theme(request):
    """AJAX endpoint to switch theme."""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        theme = data.get('theme', 'midnight')
        valid = ['noir', 'forest', 'paper', 'midnight', 'blush', 'mocha']
        if theme in valid:
            profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
            profile_obj.theme = theme
            profile_obj.save()
            return JsonResponse({'status': 'ok', 'theme': theme})
    return JsonResponse({'status': 'error'}, status=400)
