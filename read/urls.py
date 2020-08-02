from django.urls import path

from buzzword.utils import management_handling


app_name = "read"


if not management_handling():
    from .views import epub_view
    urlpatterns = [
        path("", epub_view, name="epub_view"),
        path("<str:slug>/", epub_view, name="epub_view"),
    ]
else:
    urlpatterns = []
