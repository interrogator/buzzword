from django.conf import settings
from django.shortcuts import render
from explore.models import Corpus


def example(request, slug=None):
    specific_nav = False
    if slug is None:
        from .app import app
        slug = settings.BUZZWORD_SPECIFIC_CORPUS
        specific_nav = True
        corpus = Corpus.objects.get(slug=slug)
        context = {"specific_nav": specific_nav, "navbar": "example", "corpus": corpus}
        return render(request, f"example/{slug}.html", context)
    else:
        context = {"specific_nav": False, "navbar": "example"}
        return render(request, f"example/example.html", context)

