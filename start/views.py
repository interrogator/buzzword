import os

from django.conf import settings
from django.shortcuts import render
import explore.models
from django.contrib.auth.decorators import login_required
from bootstrap_modal_forms.generic import BSModalCreateView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate


def _get_markdown_content(slug, page):
    """
    Load a markdown file
    """
    mdfile = os.path.join("static", slug, page + ".md")
    with open(mdfile, "r") as fo:
        data = fo.read()
    return data


def start(request):
    """
    Load the list-of-corpora style mainpage
    """
    navbar = request.GET.get("navbar", "home")
    corpora = explore.models.Corpus.objects.filter(disabled=False, load=True)
    context = {"corpora": corpora, "navbar": navbar}
    return render(request, "start/start.html", context)


def start_specific(request, slug=None):
    """
    Load a unique website for this particular slug

    This function also handles the example page. Genius.
    """
    slug = slug or settings.BUZZWORD_SPECIFIC_CORPUS
    current_section = request.path.strip("/")
    go_home = {"login", "logout", "signup", "corpus_settings"}
    if any(i in current_section for i in go_home) or not current_section:
        current_section = "home"
    corpus = explore.models.Corpus.objects.get(slug=slug)
    content = _get_markdown_content(slug, current_section)
    context = {"corpus": corpus, "navbar": current_section, "content": content}
    specific = "" if not settings.BUZZWORD_SPECIFIC_CORPUS else "-specific"
    return render(request, f"start/start{specific}.html", context)
