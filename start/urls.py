from django.urls import path

from . import views

app_name = "start"
urlpatterns = [
    path("", views.start, name="start"),
    path("<str:slug>/", views.start_specific, name="start_specific"),
]
