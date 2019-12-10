from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms

import explore.models

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
    return redirect('/')

def corpus_settings(request):
    fields = ('name', 'desc')
    formset_factory = forms.modelformset_factory(explore.models.Corpus, fields=fields, extra=0)
    
    if request.method == 'POST':
        formset = formset_factory(request.POST)
        if formset.is_valid():
            formset.save()
    
    corpora = explore.models.Corpus.objects.all()
    formset = formset_factory(queryset=corpora)
    context = {
        'corpora': corpora,
        'formset': formset,
    }
    return render(request, 'accounts/corpus_settings.html', context)

