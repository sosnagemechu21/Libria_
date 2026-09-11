from django.shortcuts import render, redirect
from datetime import datetime


def landing(request):
    if request.user.is_authenticated:
        return redirect('progress:dashboard')
    return render(request, 'core/landing.html')


def about(request):
    return render(request, 'core/about.html')
