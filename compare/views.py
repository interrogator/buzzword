import os

from django.shortcuts import render, redirect

from django.http import FileResponse, Http404, HttpResponse
from django.template import loader
from .models import Post
from .forms import PostForm, SimpleForm
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
        form = CompareForm(request.POST)
        if form.is_valid():
            new_text = form.cleaned_data["content"]
            commit = form.cleaned_data["commit_msg"]
            print("SUBMITTED", new_text, commit)
            buzz_raw_text = markdown_to_buzz_input(new_text)
            # save this text somewhere good
            return redirect("/")
    return HttpResponse(template.render(context, request))


def home_redirect_view(request):
    return redirect("simple_form")


def simple_form_view(request):
    form = SimpleForm()
    context = {"form": form, "title": "Simple Form"}
    return render(request, "custom_form.html", context)


def home_redirect_view(request):
    return redirect("simple_form")


@login_required
def post_form_view(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            title = form.cleaned_data["title"]
            return HttpResponse("%s successfully  saved!" % title)
    else:
        form = PostForm()
        context = {"form": form, "title": "Post Form"}
    return render(request, "custom_form.html", context)


def test_markdownify(request):
    post = Post.objects.last()
    context = {"post": post}
    if post is None:
        context = {
            "post": {
                "title": "Fake Post",
                "description": """It **working**! :heart: [Python Learning](https://python.web.id)""",
            }
        }
    return render(request, "test_markdownify.html", context)
