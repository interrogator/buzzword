import os

import django
from django.contrib.auth.decorators import login_required
from django.conf import settings

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from .forms import PostForm, SubmitForm
from .models import PDF, OCRUpdate
from .utils import markdown_to_buzz_input, store_buzz_raw

from buzzword.utils import _make_message
from explore.models import Corpus


@login_required
def browse_collection(request, slug=None):
    """
    Main compare/correct view, showing PDF beside its OCR output

    Use Django's pagination for handling PDFs
    Use martor for the markdown editor
    """
    # corpus = Corpus.objects.get(slug=slug)
    # lang = corpus.language.name
    # handle specific mode
    if not slug:
        slug = settings.BUZZWORD_SPECIFIC_CORPUS
    all_pdfs = PDF.objects.all()
    paginator = Paginator(all_pdfs, 1)
    query = request.GET.get('q')
    if query:
        page_number = int(query)
    else:
        page_number = int(request.GET.get("page", 1))
    page_obj = paginator.get_page(page_number)
    pdf = all_pdfs.get(slug=slug, num=page_number - 1)
    pdf_path = os.path.relpath(pdf.path)
    template = loader.get_template("compare/sidetoside.html")
    # get all the updates for this particular pdf
    this_pdf = OCRUpdate.objects.filter(pdf=pdf)
    # of these, get the latest ocr update submitted by this user
    user_latest = this_pdf.filter(username=request.user.username)
    if user_latest:
        user_latest = user_latest.latest("timestamp")
    # also get the latest ACCEPTED ocr
    regular_latest = this_pdf.filter(accepted=True).latest("timestamp")
    # if there is a user latest, and it's newer than the latest accepted, show that
    if user_latest and user_latest.timestamp >= regular_latest.timestamp:
        plaintext = user_latest.text
    # otherwise, show the latest accepted text
    else:
        plaintext = regular_latest.text

    default_commit = f"Update {os.path.splitext(os.path.basename(pdf_path))[0]}"
    form_data = {"description": plaintext, "commit_msg": default_commit}
    form = PostForm(initial=form_data)
    context = {
        "pdf_filepath": "/" + pdf_path.replace(".tif", ".pdf"),
        "form": form,
        "page_obj": page_obj,
        "specific_nav": bool(settings.BUZZWORD_SPECIFIC_CORPUS),
        "corpus": Corpus.objects.get(slug=slug),
        "navbar": "compare",
    }
    # if the user has tried to update the OCR text
    if request.method == "POST":
        error = False
        form = SubmitForm(request.POST)
        new_text = form["description"].value()
        commit_msg = form["commit_msg"].value()

        if new_text.strip() == plaintext.strip():
            error = "No changes made -- doing nothing"
            _make_message(request, messages.WARNING, error)

        # success case: update the db
        if form.is_valid() and not error:
            new_text = form.cleaned_data["description"]
            commit = form.cleaned_data["commit_msg"]
            buzz_raw_text = markdown_to_buzz_input(new_text, slug)
            # this updates the text file with the latest data. bad idea?
            # store_buzz_raw(buzz_raw_text, slug, pdf_path)
            # todo: handle submitted changes properly
            try:
                user = User.objects.get(id=request.user.id)
            except django.contrib.auth.models.User.DoesNotExist:
                user = None
            updated = OCRUpdate(slug=slug,
                commit_msg=commit,
                text=new_text,
                previous=plaintext,
                pdf=pdf,
                username=request.user.username,
                user=user,
                # superuser corrections are automatically accepted
                accepted=request.user.is_superuser
            )
            updated.save()
            initial = {"description": new_text, "commit_msg": default_commit}
            context["form"] = PostForm(initial=initial)
            msg = "Text successfully updated"
            if commit:
                msg = f"{msg}: {commit} ({str(updated.timestamp).split('.', 1)[0]})"
            _make_message(request, messages.SUCCESS, msg)
        else:
            # user must enter commit msg (but default is provided so it's easy)
            if not commit_msg:
                msg = "Please provide a description of your changes before updating"
                _make_message(request, messages.WARNING, msg)
            if not new_text:
                # i think this is the only possible invalid
                msg = 'No text submitted. Mark blank files with <meta blank="true"/>'
                _make_message(request, messages.WARNING, msg)

    return HttpResponse(template.render(context, request))
