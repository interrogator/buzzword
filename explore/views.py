from django.shortcuts import render
from explorer.parts.main import app, load_layout


def explore(request, slug):
    app = load_layout(slug)
    return render(request, 'explore/explore.html')
