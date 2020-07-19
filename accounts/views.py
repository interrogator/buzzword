from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django import forms

from django.conf import settings
from django.http import HttpResponseRedirect

from .forms import CustomUserCreationForm

import explore.models
from start.views import start_specific
from buzzword.utils import _make_message
from django.template import loader
from django.http import HttpResponse

def logout_view(request):
    logout(request)
    slug = settings.BUZZWORD_SPECIFIC_CORPUS
    return start_specific(request, slug=slug)


def login_view(request):
    slug = settings.BUZZWORD_SPECIFIC_CORPUS
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    context = {"slug": slug}
    print("TEMPLATE", slug)
    template = loader.get_template(f"start/{slug}.html")
    if user:
        login(request, user)
    else:
        error = "Login unsuccessful. Please sign up or try again."
        _make_message(request, messages.ERROR, error)
    return HttpResponse(template.render(context, request))


def corpus_settings(request):
    fields = ("name", "desc")
    formset_factory = forms.modelformset_factory(
        explore.models.Corpus, fields=fields, extra=0
    )

    if request.method == "POST":
        formset = formset_factory(request.POST)
        if formset.is_valid():
            formset.save()

    corpora = explore.models.Corpus.objects.all()
    formset = formset_factory(queryset=corpora)
    context = {
        "corpora": corpora,
        "formset": formset,
    }
    return render(request, "accounts/corpus_settings.html", context)


def signup(request):
    """
    Signup modal
    """
    # todo: swisslaw only
    slug = settings.BUZZWORD_SPECIFIC_CORPUS
    current_section = request.path.strip("/") or "home"
    corpus = explore.models.Corpus.objects.get(slug=slug)
    context = {}
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # save user in db...login
            form.request = request
            user = form.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
            # or redirect?
        return start_specific(request, slug=slug)


        
    else:
        form = CustomUserCreationForm()
        context["form"] = form

    return render(request, 'signup.html', context)
