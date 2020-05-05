from django.shortcuts import render
import explore.models


def start(request):
    context = {
        "corpora": explore.models.Corpus.objects.filter(disabled=False, load=True)
    }
    return render(request, "start/start.html", context)
