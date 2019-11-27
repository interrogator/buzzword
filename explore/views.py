from django.shortcuts import render
from explorer.parts.main import load_layout


def explore(request, slug):
    load_layout(slug)
    return render(request, 'explore/explore.html')
