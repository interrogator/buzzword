import os

from django.shortcuts import render
import explore.models


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


def start_specific(request, slug):
	"""
	Load a unique website for this particular slug
	"""
    navbar = request.GET.get("navbar", "home")
    corpus = explore.models.Corpus.objects.get(slug=slug)
    content = _get_markdown_content(slug, navbar)
    context = {"corpus": corpus, "navbar": navbar, "content": content}
    return render(request, f"start/start-{slug}.html", context)
