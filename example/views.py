from django.conf import settings
from django.shortcuts import render
from .app import app

# Create your views here.


#@login_required
def example(request, slug=None):
    if slug is None:
        slug = settings.BUZZWORD_SPECIFIC_CORPUS
    return render(request, "example/example.html")