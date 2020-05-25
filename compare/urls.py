from django.urls import path


from .views import browse_collection

urlpatterns = [
    path("<str:slug>/", browse_collection, name="browse_collection"),
]
