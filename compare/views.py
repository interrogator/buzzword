from django.shortcuts import render, redirect

from django.http import FileResponse, Http404, HttpResponse
from django.template import loader
from .models import Post
from .forms import PostForm, SimpleForm
from .utils import filepath_for_pdf, markdown_to_buzz_input, get_raw_text_for_ocr
from django.contrib.auth.decorators import login_required

PDF_FILE = "/static/testpage.pdf"


def browse_collection(request):
    template = loader.get_template("compare/sidetoside.html")
    initial_textbox = dict(description=get_raw_text_for_ocr(PDF_FILE))
    context = {
        "pdf_filepath": PDF_FILE,
        "file_showing": filepath_for_pdf(PDF_FILE),
        "form": PostForm(),
    }
    return HttpResponse(template.render(context, request))
    """
    if request.method == "POST":
        form = CompareForm(request.POST)
        if form.is_valid():
            new_text = form.cleaned_data["content"]
            commit = form.cleaned_data["commit_msg"]
            print("SUBMITTED", new_text, commit)
            buzz_raw_text = markdown_to_buzz_input(new_text)
            # save this text somewhere good
           SSSSSSSSSSSSSSSSSSSSSSSSS return redirect("/")
    """


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
