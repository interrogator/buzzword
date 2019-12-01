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
    class CSForm(forms.Form):
        def __init__(self, corpora):
            super().__init__()
            for corpus in corpora:
                self.fields[f'disabled[{corpus.id}]'] = forms.BooleanField(initial=corpus.disabled, label=corpus.name)

    corpora = explore.models.Corpus.objects.all()
    context = {
        'corpora': corpora,
        'form': CSForm(corpora),
    }
    return render(request, 'accounts/corpus_settings.html', context)

