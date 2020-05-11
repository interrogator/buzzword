from django.shortcuts import render

from django.http import FileResponse, Http404, HttpResponse
from django.template import loader


def browse_collection(request):
    template = loader.get_template("compare/sidetoside.html")
    context = {"pdf_name": "../testpage.pdf", "plaintext": "lorem ipsum"}
    return HttpResponse(template.render(context, request))
