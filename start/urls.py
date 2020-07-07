from django.urls import path, re_path

from . import views
from explore.models import Corpus
from django.conf import settings

# we need to make a regex matching each corpus slug
# so that signout and other urls are still matched
slugs = [i.slug for i in Corpus.objects.all()]
slugs = "(" + "|".join(set(slugs)) + ")"
paths = f"^(?P<slug>{slugs})/"

app_name = "start"

# in specific mode, disallow the homepage, redirecting always to the specific
if not settings.BUZZWORD_SPECIFIC_CORPUS:
    urlpatterns = [path("", views.start, name="start")]
else:
	slug = dict(slug=settings.BUZZWORD_SPECIFIC_CORPUS)
	urlpatterns = [path("", views.start_specific, slug)]

urlpatterns.append(re_path(paths, views.start_specific, name="start_specific"))
