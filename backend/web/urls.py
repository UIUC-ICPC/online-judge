from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
    path("contests/", views.contests, name="contests"),
    path("problems/", views.problems, name="problems"),
    path("ratings/", views.ratings, name="ratings"),
    path("profile/", views.profile, name="profile"), 
    path("problems/<int:problem_id>/submissions/", views.problem_submissions, name="problem_submissions"),
    path("problems/submissions/", views.all_recent_submissions, name="all_recent_submissions"),
]
