import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from explore.models import Corpus


#@login_required
def epub_view(request, slug=None):
    corpus = Corpus.objects.get(slug=slug)
    epub_path = os.path.join(corpus.path, "epub")
    epub = next(i for i in os.listdir(epub_path) if i.endswith((".epub", "opf")))
    epub_path = os.path.join("/", epub_path, epub)
    template = loader.get_template("read/read.html")
    context = {"corpus": corpus, "epub": epub_path}
    return HttpResponse(template.render(context, request))
