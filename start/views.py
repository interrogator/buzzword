from django.http import HttpResponse
from django.shortcuts import render


def start(request):
    return render(request, 'start/start.html')
