from django.urls import path

from . import views

app_name = "explore"
urlpatterns = [
    path("", views.explore, name="explore"),
    path("<str:slug>/", views.explore, name="explore"),
    path("upload", views.upload, name="upload"),
]
