from django.urls import path, re_path

from explore.models import Corpus
from django.conf import settings
from buzzword.utils import management_handling


app_name = "start"


def _register_urls():
    from . import views
    # we need to make a regex matching each corpus slug
    # so that signout and other urls are still matched
    # try-except is to catch migrate (etc) calls
    slugs = [i.slug for i in Corpus.objects.all()]

    slugs = "(" + "|".join(set(slugs)) + ")"
    paths = f"^(?P<slug>{slugs})/"

    urlpatterns = [
        re_path(paths, views.start_specific, name="start_specific"),
        path("user/<str:username>/", views.user_profile, name="user_profile")
    ]

    # in specific mode, disallow the homepage, redirecting always to the specific
    if not settings.BUZZWORD_SPECIFIC_CORPUS:
        urlpatterns += [path("", views.start, name="start")]
    else:
        pages = {"", "about/", "howto/"}
        urlpatterns += [path(x, views.start_specific) for x in pages]
    return urlpatterns


if management_handling():
    urlpatterns = []
else:
    urlpatterns = _register_urls()
