from django.shortcuts import render, redirect
from explorer.parts.main import app, load_layout
from django import forms
from explore.models import Corpus
from explorer.parts.strings import _slug_from_name

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

def explore(request, slug):
    app = load_layout(slug)
    return render(request, "explore/explore.html")

def upload_corpus(request):
    class UploadCorpusForm(forms.ModelForm):
        class Meta:
            model = Corpus
            fields = ["name", "desc", "language", "date", "url"]
        corpus_file = forms.FileField()
    
    if request.method == "POST":
        form = UploadCorpusForm(request.POST, request.FILES)
        if form.is_valid():
            slug = _slug_from_name(form.cleaned_data["name"])
            try:
                path = _store_corpus_file(request.FILES["corpus_file"], slug)
            except:
                # TODO: was not able to store corpus file. possibly duplicate slug. handle gracefully
                raise
            corpus = form.save(commit=False)
            corpus.slug = slug
            corpus.path = path
            corpus.save()
            _start_parse_corpus_job(corpus)
            return redirect("/")
    else:
        form = UploadCorpusForm()

    return render(request, "explore/upload_corpus.html", {
        "form": form,
    })
