from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from explore.models import Corpus
from explorer.main import load_layout
from explorer.helpers import register_callbacks
from explorer.strings import _slug_from_name
from .forms import UploadCorpusForm

from django.conf import settings

def _make_path(slug):
    return f"storage/{slug}"


def _store_corpus_file(corpus_file, slug):
    """
        store the corpus file sent by the user
        in the local storage. fails if a corpus with
        the same slug already exists.
    """
    path = _make_path(slug)
    with open(_make_path(slug), "xb") as storage:
        for chunk in corpus_file.chunks():
            storage.write(chunk)
    return path


def _start_parse_corpus_job(corpus):
    # todo: implement this function
    pass



@login_required
def explore(request, slug=None):
    from explorer.main import app
    register_callbacks()
    if slug is None:
        slug = settings.BUZZWORD_SPECIFIC_CORPUS
    context = {"corpus": Corpus.objects.get(slug=slug)}
    return render(request, "explore/explore.html", context=context)


@login_required
def upload(request):
    if request.method == "POST":
        form = UploadCorpusForm(request.POST, request.FILES)
        if form.is_valid():
            slug = _slug_from_name(form.cleaned_data["name"])
            try:
                path = _store_corpus_file(request.FILES["corpus_file"], slug)
            except Exception:
                # TODO: was not able to store corpus file. possibly duplicate slug.
                # handle gracefully
                raise
            corpus = form.save(commit=False)
            corpus.slug = slug
            corpus.path = path
            corpus.save()
            _start_parse_corpus_job(corpus)
            return redirect("/")
    else:
        form = UploadCorpusForm()

    context = {"form": form, "navbar": "upload"}

    return render(request, "explore/upload.html", context)
