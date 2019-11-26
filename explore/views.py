from django.http import HttpResponse
from django.shortcuts import render
from explorer.__main__ import CORPORA_CONFIGS, _get_explore_layout, app


def explore(request, slug):
    print('SLUG', slug)
    print('APP', app)
    app.layout = _get_explore_layout(slug, CORPORA_CONFIGS)
    return render(request, 'explore/explore.html')
