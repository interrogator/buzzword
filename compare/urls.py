from django.urls import path


from .views import browse_collection

urlpatterns = [
    path("", browse_collection, name="browse_collection"),
    path("<str:slug>/", browse_collection, name="browse_collection"),
]
