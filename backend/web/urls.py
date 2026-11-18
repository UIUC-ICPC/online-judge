from django.urls import path
from . import views, worker_views

app_name = "web"

urlpatterns = [
    path("worker/task", worker_views.finished_judging_task, name="finished_task"),
    path("", views.home, name="home"),
    path("contests/", views.contests, name="contests"),
    path("problems/", views.problems, name="problems"),
    path("ratings/", views.ratings, name="ratings"),
    path("profile/", views.profile, name="profile"),
    path("contests/<int:contest_id>/", views.contest_detail, name="contest_detail"),
    path(
        "contests/<int:contest_id>/standings",
        views.contest_standings,
        name="contest_standings",
    ),
    path("profile/", views.profile, name="profile"),
    path("contests/<int:contest_id>/my", views.contest_my, name="contest_my"),
    path(
        "contests/<int:contest_id>/problems/<str:problem_label>",
        views.contest_problem_page,
        name="contest_problem_page",
    ),
    path(
        "contests/register/<int:contest_id>/problems/<str:problem_label>/submit/",
        views.contest_problem_submit,
        name="contest_problem_submit",
    ),
    path(
        "contests/register/<int:contest_id>/submit/",
        views.contest_register,
        {"register": True},
        name="contest_register",
    ),
    path(
        "contests/register/<int:contest_id>/cancel/",
        views.contest_register,
        {"register": False},
        name="contest_unregister",
    ),
    path(
        "problems/<int:problem_id>/submissions/",
        views.problem_submissions,
        name="problem_submissions",
    ),
    path(
        "problems/submissions/",
        views.all_recent_submissions,
        name="all_recent_submissions",
    ),
    path(
        "submissions/count/",
        views.number_of_submissions_from_team,
        name="number_of_submissions_from_team",
    ),
]
