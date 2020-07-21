from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout, authenticate
from accounts.context_processors import CustomAuthForm
from django import forms

from django.conf import settings
from django.http import HttpResponseRedirect

from .forms import CustomUserCreationForm

from accounts.context_processors import CustomAuthForm
from explore.models import Corpus
from start.views import start_specific, _get_markdown_content
from buzzword.utils import _make_message
from django.template import loader
from django.http import HttpResponse


def logout_view(request):
    logout(request)
    slug = settings.BUZZWORD_SPECIFIC_CORPUS
    return start_specific(request, slug=slug)


def login(request):
    slug = settings.BUZZWORD_SPECIFIC_CORPUS
    username = request.POST.get("username")
    password = request.POST.get("password")
    nextpage = request.GET.get("next")

    # next page means we need to authenticate them and send to nextpage
    if nextpage:

        error = f"Registration/login required for the {nextpage.strip('/').capitalize()} page."
        _make_message(request, messages.WARNING, error)
        corpus = Corpus.objects.get(slug=slug)
        content = _get_markdown_content(slug, "home")
        context = {"corpus": corpus, "navbar": "home", "content": content}
        return render(request, f"start/{slug}.html", context)

    user = authenticate(request, username=username, password=password)
    nextpage = nextpage or f"start/{slug}.html"
    template = loader.get_template(nextpage)
    go_home = {"login", "logout", "signup", "corpus_settings"}
    corpus = Corpus.objects.get(slug=slug)
    current_section = None  # todo
    if current_section in go_home or not current_section:
        current_section = "home"
    content = _get_markdown_content(slug, current_section)
    context = {"corpus": corpus, "navbar": current_section, "content": content}
    if user:
        django_login(request, user)
    else:
        error = "Login unsuccessful. Please sign up or try again."
        _make_message(request, messages.WARNING, error)
    return HttpResponse(template.render(context, request))


def corpus_settings(request):
    fields = ("name", "desc")
    formset_factory = forms.modelformset_factory(
        Corpus, fields=fields, extra=0
    )

    if request.method == "POST":
        formset = formset_factory(request.POST)
        if formset.is_valid():
            formset.save()

    corpora = Corpus.objects.all()
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
    corpus = Corpus.objects.get(slug=slug)
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
                django_login(request, user)
            # or redirect?
        return start_specific(request, slug=slug)
    else:
        form = CustomUserCreationForm()
        context["form"] = form

    return render(request, 'signup.html', context)
