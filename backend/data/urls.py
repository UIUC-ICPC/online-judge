from django.urls import path
from . import views

# list of endpoints where all our apis will be described on
urlpatterns = [
  path("", views.index, name="index"),
]