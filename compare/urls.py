from django.urls import path

from . import views

urlpatterns = [
    path("", views.browse_collection, name="browse_collection"),
]
