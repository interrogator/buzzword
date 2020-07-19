from django.urls import path

from . import views

from buzzword.utils import management_handling

app_name = "example"

if management_handling():
    urlpatterns = []
else:
    urlpatterns = [
        path("", views.example, name="example"),
    ]
