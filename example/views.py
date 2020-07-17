from django.conf import settings
from django.shortcuts import render
from .app import app
from explore.models import Corpus


def example(request, slug=None):
    specific_nav = False
    if slug is None:
        slug = settings.BUZZWORD_SPECIFIC_CORPUS
        specific_nav = True
    corpus = Corpus.objects.get(slug=slug)
    context = {"specific_nav": specific_nav, "navbar": "example", "corpus": corpus}
    return render(request, "example/example.html", context)
