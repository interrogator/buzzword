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
from .utils import markdown_to_buzz_input, store_buzz_raw, _get_sections

from buzzword.utils import _make_message
from explore.models import Corpus



def _latest_ocrupdate(pdf, username):
    ocrs = OCRUpdate.objects.filter(pdf=pdf)
    # of this pdf, get the latest ocr update submitted by this user
    user_latest = ocrs.filter(username=username)
    if user_latest:
        user_latest = user_latest.latest("timestamp")
    # also get the latest ACCEPTED ocr
    regular_latest = ocrs.filter(accepted=True).latest("timestamp")
    # if there is a user latest, and it's newer than the latest accepted, show that
    if user_latest and user_latest.timestamp >= regular_latest.timestamp:
        return user_latest
    # otherwise, show the latest accepted text
    else:
        return regular_latest


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
    sections = _get_sections(slug)
    text_search = request.GET.get("search")
    search_results = None
    if text_search:
        search_results = _text_search(text_search, slug, request.user.username, sections)
        if not search_results:
            msg = "No results found, sorry."
            _make_message(request, messages.WARNING, msg)
    page_obj = paginator.get_page(page_number)
    pdf = all_pdfs.get(slug=slug, num=page_number - 1)
    pdf_path = os.path.relpath(pdf.path)
    template = loader.get_template("compare/sidetoside.html")
    # get all the updates for this particular pdf
    plaintext = _latest_ocrupdate(pdf, username=request.user.username).text
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
        "text_search": search_results,
        "sections": sections,
        "colwidth": "48vw" if not sections else "40vw",
        "coldata": "-5" if sections else "",
        "search_query": text_search
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


def _get_book_and_chapter(pdf, sections):
    for book, info in sections.items():
        chapter_names = list(info["chapters"])
        for i, (chapter, subinfo) in enumerate(info["chapters"].items()):
            # todo: inclusive exclusive?
            end = subinfo.get("end")
            if end is None:
                # if this is the last chapter
                if i == len(info["chapters"]) - 1:
                    end = info["end"]
                else:
                    # get next chapter name
                    nxt = info["chapters"][chapter_names[i+1]]
                    # get either its end or its start-1
                    end = nxt["start"]-1 if isinstance(nxt, dict) else nxt-1
            if subinfo["start"] <= pdf.num <= end:
                return book, chapter
    for book, info in sections.items():
        if pdf.num >= info["start"] <= info["end"]:
            return book, ""
    return "", ""


def _text_search(query, slug, username, sections):
    """
    get or create a search, returning the resulting queryset

    todo: store user's latest 'update' and 
    """
    # exists = TextSearches.objects.get(corpus=corpus, query=query)
    corpus = Corpus.objects.get(slug=slug)
    exists = False
    has_not_updated = False  # todo
    query = query.lower()
    if exists and has_not_updated:
        all_pdfs = exists.pdfs_set.all()
        results = [(pdf, _latest_ocrupdate(pdf, username=username).text) for pdf in all_pdfs]
    else:
        all_pdfs = PDF.objects.filter(slug=slug)
        results = []
        for pdf in all_pdfs:
            plaintext = _latest_ocrupdate(pdf, username=username).text
            plain_low = plaintext.lower()
            occurrences = plain_low.count(query)
            if not occurrences:
                continue
            for i in range(occurrences):
                index = plain_low.index(query)            
                title = ""
                book, chapter = _get_book_and_chapter(pdf, sections)
                page = pdf.num+1
                left = plaintext[max(0, index-120):index].replace("\n", " ")
                right = plaintext[index+len(query):index+len(query)+120].replace("\n", " ")
                line = dict(
                    left=left,
                    match=plaintext[index:index+len(query)],
                    right=right,
                    title=title,
                    page=page,
                    book=book,
                    chapter=chapter
                )
                results.append(line)
                plaintext = plaintext[index+len(query):]
                plain_low = plain_low[index+len(query):]
    return results
