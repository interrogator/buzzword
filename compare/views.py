import os

from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template import loader

from .forms import PostForm, SubmitForm
from .models import PDF, OCRUpdate
from .utils import markdown_to_buzz_input, store_buzz_raw

from explore.models import Corpus


def _make_message(request, level, msg):
    """
    Just add the message once
    """
    if msg not in [m.message for m in get_messages(request)]:
        messages.add_message(request, level, msg)


def browse_collection(request, slug):
    """
    Main compare/correct view, showing PDF beside its OCR output

    Use Django's pagination for handling PDFs
    Use martor for the markdown editor
    """
    # corpus = Corpus.objects.get(slug=slug)
    # lang = corpus.language.name
    spec = bool(settings.BUZZWORD_SPECIFIC_CORPUS)
    all_pdfs = PDF.objects.all()
    paginator = Paginator(all_pdfs, 1)
    page_number = request.GET.get("page", 1)
    page_number = int(page_number)
    page_obj = paginator.get_page(page_number)
    pdf = all_pdfs.get(slug=slug, num=page_number - 1)
    pdf_path = pdf.path
    template = loader.get_template("compare/sidetoside.html")

    this_pdf = OCRUpdate.objects.filter(pdf=pdf)
    plaintext = this_pdf.latest("timestamp").text

    default_commit = f"Update {os.path.splitext(os.path.basename(pdf_path))[0]}"
    form = PostForm(initial={"description": plaintext, "commit_msg": default_commit})
    context = {
        "pdf_filepath": "/" + pdf_path.replace(".tif", ".pdf"),
        "form": form,
        "page_obj": page_obj,
        "specific_nav": spec,
        "corpus": Corpus.objects.get(slug=slug),
        "navbar": "compare"
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
            store_buzz_raw(buzz_raw_text, slug, pdf_path)
            # todo: handle submitted changes properly
            updated = OCRUpdate(slug=slug, commit_msg=commit, text=new_text, pdf=pdf)
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
