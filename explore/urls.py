from django.urls import path

from . import views

app_name = 'explore'
urlpatterns = [
    path('<str:slug>/', views.explore, name="explore"),
]
