import os
from datetime import datetime
from django.shortcuts import render, redirect

from django.http import FileResponse, Http404, HttpResponse
from django.template import loader
from .models import Post
from .forms import PostForm, SubmitForm
from .utils import (
    markdown_to_buzz_input,
    get_raw_text_for_ocr,
    _get_pdf_paths,
)
from django.contrib.auth.decorators import login_required


from django.core.paginator import Paginator
from django.shortcuts import render

from .models import PDF, OCRUpdate

from django.contrib import messages


def browse_collection(request, slug):
    all_pdfs = PDF.objects.all()
    paginator = Paginator(all_pdfs, 1)
    page_number = request.GET.get("page", 1)
    page_number = int(page_number)
    page_obj = paginator.get_page(page_number)
    # can i get without second lookup using paginator?
    pdf = PDF.objects.get(slug=slug, num=page_number - 1)
    pdf_path = pdf.path
    template = loader.get_template("compare/sidetoside.html")
    plaintext = get_raw_text_for_ocr(slug, pdf)
    initial_textbox = dict(description=plaintext)
    form = PostForm(initial={"description": plaintext})
    context = {
        "pdf_filepath": "/" + pdf_path,
        # "file_showing": filepath_for_pdf(pdf),
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
            updated = OCRUpdate(slug=slug, commit_msg=commit, text=new_text, pdf=pdf)
            updated.save()
            context["form"] = PostForm(initial={"description": new_text})
            msg = "Text successfully updated"
            if commit:
                # timestamp = datetime.fromtimestamp(updated.timestamp)
                msg = f"{msg}: {commit} ({updated.timestamp})"
            messages.add_message(request, messages.SUCCESS, msg)
        else:
            messages.add_message(request, messages.WARNING, "Invalid form.")
    return HttpResponse(template.render(context, request))
