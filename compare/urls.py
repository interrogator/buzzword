from django.urls import path

from .views import browse_collection

from buzz.utils import management_handling


app_name = "compare"


if not management_handling():
    urlpatterns = [
        path("", browse_collection, name="browse_collection"),
        path("<str:slug>/", browse_collection, name="browse_collection"),
    ]
else:
    urlpatterns = []
