from django.urls import path


from .views import (
    home_redirect_view,
    simple_form_view,
    post_form_view,
    test_markdownify,
    browse_collection,
)

urlpatterns = [
    path("<str:slug>/", browse_collection, name="browse_collection"),
    path("simple-form/", simple_form_view, name="simple_form"),
    path("post-form/", post_form_view, name="post_form"),
    path("test-markdownify/", test_markdownify, name="test_markdownify"),
]
