import os

from django.shortcuts import render, redirect

from django.http import FileResponse, Http404, HttpResponse
from django.template import loader
from .models import Post
from .forms import PostForm, SubmitForm
from .utils import (
    filepath_for_pdf,
    markdown_to_buzz_input,
    get_raw_text_for_ocr,
    _get_pdf_paths,
)
from django.contrib.auth.decorators import login_required


from django.core.paginator import Paginator
from django.shortcuts import render

from .models import PDF

from django.contrib import messages


def browse_collection(request, slug):
    contact_list = PDF.objects.all()
    paginator = Paginator(contact_list, 1)
    page_number = request.GET.get("page", 1)
    page_number = int(page_number)
    page_obj = paginator.get_page(page_number)
    pdfs = _get_pdf_paths(slug)
    pdf_file = pdfs[int(page_number) - 1]  # static root ... do this better
    template = loader.get_template("compare/sidetoside.html")
    plaintext = get_raw_text_for_ocr(slug, pdf_file)
    initial_textbox = dict(description=plaintext)
    form = PostForm(initial={"description": plaintext})
    context = {
        "pdf_filepath": "/" + pdf_file,
        "file_showing": filepath_for_pdf(pdf_file),
        "form": form,
        "page_obj": page_obj,
    }
    if request.method == "POST":
        form = SubmitForm(request.POST)
        new_text = form["description"].value()
        commit_msg = form["commit_msg"].value()
        if new_text.strip() == plaintext.strip():
            messages.add_message(
                request, messages.WARNING, "No changes made; doing nothing"
            )
        elif not commit_msg:
            messages.add_message(
                request,
                messages.WARNING,
                "No change information provided; doing nothing",
            )

        if form.is_valid():
            new_text = form.cleaned_data["description"]
            commit = form.cleaned_data["commit_msg"]
            buzz_raw_text = markdown_to_buzz_input(new_text)
            # todo: handle submitted changes properly
            context["form"] = PostForm(initial={"description": new_text})
            messages.add_message(request, messages.SUCCESS, "Text updated.")
        else:
            messages.add_message(request, messages.WARNING, "Invalid form.")
    return HttpResponse(template.render(context, request))
