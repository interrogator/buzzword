from django.urls import path

from . import views

app_name = "explore"
urlpatterns = [
    path("<str:slug>/", views.explore, name="explore"),
    path("upload_corpus", views.upload_corpus, name="upload_corpus"),
]
