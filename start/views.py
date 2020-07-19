import os

from django.conf import settings
from django.shortcuts import render
import explore.models
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from bootstrap_modal_forms.generic import BSModalCreateView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.db.utils import OperationalError

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

#@login_required
def start_specific(request, slug=None):
    """
    Load a unique website for this particular slug

    This function also handles the example page. Genius.
    """
    slug = slug or settings.BUZZWORD_SPECIFIC_CORPUS
    current_section = request.path.strip("/") or "home"
    corpus = explore.models.Corpus.objects.get(slug=slug)
    content = _get_markdown_content(slug, current_section)
    context = {"corpus": corpus, "navbar": current_section, "content": content}
    return render(request, f"start/{slug}.html", context)


class SignUpView(BSModalCreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_message = 'Sign up succeeded. You can now log in.'
    slug = settings.BUZZWORD_SPECIFIC_CORPUS  # todo: slug for non specific
    # when trying to do initial migrate, this table doesn't exist yet
    # but it is loaded because of urls.py
    try:
        corpus = explore.models.Corpus.objects.get(slug=slug)
    except OperationalError:
        corpus = None
    content = _get_markdown_content(slug, "home")
    context = {"corpus": corpus, "navbar": "home", "content": content}
    # return to homepage, logged in, authenticated
    # return render(f"start/{slug}.html", context)
    success_url = reverse_lazy("start.views.start_specific", kwargs={"slug": slug})


def signup(request, slug=None):
    # if this is a POST request we need to process the form data
    slug = slug or settings.BUZZWORD_SPECIFIC_CORPUS
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