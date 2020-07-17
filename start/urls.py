from django.urls import path, re_path

from . import views
from explore.models import Corpus
from django.conf import settings
from django.db.utils import OperationalError

# we need to make a regex matching each corpus slug
# so that signout and other urls are still matched
# try-except is to catch migrate (etc) calls
try:
    slugs = [i.slug for i in Corpus.objects.all()]
except OperationalError:
    slugs = []

slugs = "(" + "|".join(set(slugs)) + ")"
paths = f"^(?P<slug>{slugs})/"

app_name = "start"

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    re_path(paths, views.start_specific, name="start_specific")
]

# in specific mode, disallow the homepage, redirecting always to the specific
if not settings.BUZZWORD_SPECIFIC_CORPUS:
    urlpatterns += [path("", views.start, name="start")]
else:
    urlpatterns += [path("", views.start_specific)]
