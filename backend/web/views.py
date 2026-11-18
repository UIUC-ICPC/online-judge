from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_safe, require_POST
from django.db import transaction
from data.models import (
    Contest,
    Submission,
    Judging,
    ContestProblem,
    ContestParticipant,
    ContestTeam,
)
from .azure import get_blob_sas_url
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .forms import SubmissionForm
from .util import validate_contest_access
from services.dispatcher import dispatch_task


# TODO: error handling if db transaction fails
@login_required
@require_safe
def profile(request):
    return render(request, "pages/profile.html", {"profile_user": request.user})


@require_safe
def contests(request):
    now = timezone.now()
    contests = Contest.objects.prefetch_related("writers__user")
    upcoming = contests.filter(end_time__gte=now).order_by("start_time")
    past = contests.filter(end_time__lt=now).order_by("-end_time")
    
    registered_contest_ids = set()
    if request.user.is_authenticated:
        registered_contest_ids = set(
            ContestParticipant.objects.filter(user=request.user).values_list(
                "team__contest_id", flat=True
            )
        )
        
    for contest in upcoming:
        contest.registered = contest.id in registered_contest_ids

    return render(
        request,
        "pages/contest/contests.html",
        {
            "upcoming": upcoming,
            "past": past,
            "now": now,
        },
    )
    

@login_required
@require_safe
def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    validate_contest_access(request.user, contest)

    problems = (
        ContestProblem.objects.filter(contest=contest)
        .select_related("problem")
        .order_by("label")
    )

    return render(
        request,
        "pages/contest/contest_problems.html",
        {"contest": contest, "problems": problems},
    )


@login_required
@require_safe
def contest_problem_page(request, contest_id, problem_label):
    contest = get_object_or_404(Contest, id=contest_id)
    validate_contest_access(request.user, contest)

    problem = get_object_or_404(
        ContestProblem.objects.select_related("problem"),
        contest__id=contest_id,
        label=problem_label,
    )

    return _render_contest_problem(request, contest, problem, SubmissionForm())


@login_required
@require_POST
@transaction.atomic
def contest_register(request, contest_id, register):
    # TODO: enable team functionality + better way to handle "default" teams
    # ensure one team / contest is enforced
    contest = get_object_or_404(Contest.objects.select_for_update(), id=contest_id)
    if contest.start_time <= timezone.now():
        raise PermissionDenied("Contest registration is closed.")

    registered = ContestParticipant.objects.filter(
        user=request.user, team__contest=contest
    )
    if register and not registered.exists():
        ContestParticipant.objects.create(
            user=request.user,
            team=ContestTeam.objects.create(name="default", contest=contest),
        )
    elif not register and registered.exists():
        registered.delete()
        
    return redirect("web:contests")


@login_required
@require_POST
@transaction.atomic
def contest_problem_submit(request, contest_id, problem_label):
    # TODO: rate limit, prevent double click, etc
    contest = get_object_or_404(Contest, id=contest_id)
    validate_contest_access(request.user, contest) 
    
    problem = get_object_or_404(
        ContestProblem.objects.select_related("problem"),
        contest__id=contest_id,
        label=problem_label,
    )
    
    form = SubmissionForm(request.POST, request.FILES)
    if not form.is_valid():
        return _render_contest_problem(request, contest, problem, form)

    team = get_object_or_404(
        ContestTeam,
        contest_id=contest_id,
        participants__user=request.user,
    )
    submission = Submission.objects.create(
        user=request.user,
        team=team,
        contest=contest,
        problem=problem.problem,
        language=form.cleaned_data["language"],
        source_code=form.cleaned_data["source_code"],
    )
    Judging.objects.create(
        submission=submission,
        status=Judging.Status.QUEUED,
        created_at=timezone.now(),
    )
    
    transaction.on_commit(dispatch_task) 
    return redirect("web:contest_problem_page", contest_id, problem_label)


def _render_contest_problem(request, contest, problem, submission_form):
    return render(
        request,
        "pages/contest/contest_problem_page.html",
        {
            "contest": contest,
            "problem": problem,
            "statement_url": get_blob_sas_url(problem.problem.blob_name),
            "submission_form": submission_form,
        },
    )


# ---------------------------------------------------------------
# TODO: below still require either data to dynamically be fetched
# or for the respective html/css templates to actually be written/finished
@require_safe
def home(request):
    return render(request, "pages/home.html")


@require_safe
def problems(request):
    return render(request, "pages/problems.html")


@require_safe
def ratings(request):
    return render(request, "pages/ratings.html")


@require_safe
def contest_standings(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    return render(
        request,
        "pages/contest/contest_standings.html",
        {
            "contest": contest,
        },
    )


@require_safe
def contest_my(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    return render(
        request,
        "pages/contest/contest_submissions.html",
        {
            "contest": contest,
        },
    )


@require_safe
def problem_submissions(request, problem_id):
    submissions = Submission.objects.filter(problem_id=problem_id).order_by(
        "-submitted_at"
    )[:50]
    return render(
        request,
        "pages/problem_submissions.html",
        {"problem_id": problem_id, "submissions": submissions},
    )


@require_safe
def all_recent_submissions(request):
    submissions = Submission.objects.order_by("-submitted_at")[:50]
    return render(
        request, "pages/problem_submissions.html", {"submissions": submissions}
    )


@require_safe
def number_of_submissions_from_team(request):
    team_id = request.GET.get("team_id")
    submissions_count = Submission.objects.filter(team_id=team_id).count()
    return render(
        request,
        "pages/number_of_submissions_from_team.html",
        {"team_id": team_id, "submissions_count": submissions_count},
    )
