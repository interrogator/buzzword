from django.http import HttpResponse
from django.shortcuts import render
import explore.models
from guardian.shortcuts import get_objects_for_user

def start(request):
    context = {
        "corpora": get_objects_for_user(request.user, "view_corpus", explore.models.Corpus).filter(disabled=False,load=True)
    }
    return render(request, "start/start.html", context)
