from django.shortcuts import render
from explorer.parts.main import populate_explorer_with_initial_data


def explore(request, slug):
    populate_explorer_with_initial_data(slug)
    return render(request, 'explore/explore.html')
