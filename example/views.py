import os
import random

from django.conf import settings
from django.shortcuts import render

from .app import make_app, _make_layout
from explore.models import Corpus

def get_slug(slug):
    specific = bool(settings.BUZZWORD_SPECIFIC_CORPUS)
    if slug:
        return slug, specific
    if settings.BUZZWORD_SPECIFIC_CORPUS:
        return settings.BUZZWORD_SPECIFIC_CORPUS, specific
    elif settings.BUZZWORD_EXAMPLE_CORPUS:
        slug = settings.BUZZWORD_EXAMPLE_CORPUS
        if slug and slug != "random":
            return slug, specific
    # get one at random
    slugs = [c.slug for c in Corpus.objects.all()]
    while True:
        slug = random.choice(slugs)
        if os.path.exists(f"static/{slug}/example.json"):
            return slug, specific


def example(request, slug=None):
    from .callbacks import add_callbacks
    slug, specific_nav = get_slug(slug)
    corpus = Corpus.objects.get(slug=slug)
    app = make_app(slug)
    from .app import _quick_concordance, _quick_freq
    app = add_callbacks(app, slug, _quick_concordance, _quick_freq)
    app.layout = _make_layout(slug)
    title = corpus.name
    context = {"specific_nav": specific_nav, "navbar": "example", "slug": slug, "title": title}
    return render(request, f"example/example.html", context)
