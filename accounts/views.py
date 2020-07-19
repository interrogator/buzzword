from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.conf import settings
from .forms import CustomUserCreationForm

import explore.models


def logout_view(request):
    logout(request)
    return redirect("/")


def login_view(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
    return redirect("/")


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
            print("SAVED IN DB...")
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
            # or redirect?
            return render(request, f"start/{slug}.html", context)
    else:
        form = CustomUserCreationForm()
        context["form"] = form

    return render(request, 'signup.html', context)
