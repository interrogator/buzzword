from django.urls import path

from buzzword.utils import management_handling

app_name = "example"

if management_handling():
    urlpatterns = []
else:
    from . import views
    urlpatterns = [
        path("", views.example, name="example"),
    ]
