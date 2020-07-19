from django.urls import path, re_path

from . import views
from explore.models import Corpus
from django.conf import settings
from buzzword.utils import management_handling


app_name = "start"


def _register_urls():
    # we need to make a regex matching each corpus slug
    # so that signout and other urls are still matched
    # try-except is to catch migrate (etc) calls
    slugs = [i.slug for i in Corpus.objects.all()]

    slugs = "(" + "|".join(set(slugs)) + ")"
    paths = f"^(?P<slug>{slugs})/"

    urlpatterns = [
        path('signup/', views.signup, name='signup'),
        re_path(paths, views.start_specific, name="start_specific")
    ]

    # in specific mode, disallow the homepage, redirecting always to the specific
    if not settings.BUZZWORD_SPECIFIC_CORPUS:
        urlpatterns += [path("", views.start, name="start")]
    else:
        urlpatterns += [path("", views.start_specific)]
    return urlpatterns


if management_handling():
    urlpatterns = []
else:
    urlpatterns = _register_urls()
