from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_safe
from data.models import Submission


@require_safe
def home(request):
    return render(request, "pages/home.html")

@require_safe
def problem_submissions(request, problem_id):
    submissions = Submission.objects.filter(problem_id=problem_id).order_by("-submitted_at")[:50]
    return render(request, "pages/problem_submissions.html", {"problem_id": problem_id, "submissions": submissions})

@require_safe
def all_recent_submissions(request):
    submissions = Submission.objects.order_by("-submitted_at")[:50]
    return render(request, "pages/problem_submissions.html", {"submissions": submissions})

@require_safe
def number_of_submissions_from_team(request):
    team_id = request.GET.get("team_id")
    submissions_count = Submission.objects.filter(team_id=team_id).count()
    return render(request, "pages/number_of_submissions_from_team.html", {"team_id": team_id, "submissions_count": submissions_count})

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
