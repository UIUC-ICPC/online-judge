from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def home(request):
    return render(request, "pages/home.html")


@require_safe
def contests(request):
    return render(request, "pages/contests.html")


@require_safe
def problems(request):
    return render(request, "pages/problems.html")


@require_safe
def ratings(request):
    return render(request, "pages/ratings.html")


@login_required
@require_safe
def profile(request):
    return render(request, "pages/profile.html", {"profile_user": request.user})
