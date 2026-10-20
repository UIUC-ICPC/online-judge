from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
    path("contests/", views.contests, name="contests"),
    path("problems/", views.problems, name="problems"),
    path("ratings/", views.ratings, name="ratings"),
    path("profile/", views.profile, name="profile"), 
]
