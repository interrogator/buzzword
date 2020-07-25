from django import forms
from django.forms.widgets import PasswordInput, TextInput

from django.contrib.auth.forms import AuthenticationForm


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'col-md-12 small-login user-input validate form-control form-control-sm','placeholder': 'Username', "autocomplete": "username"}))
    password = forms.CharField(widget=PasswordInput(attrs={'class':'float-left mx-auto col-md-8 fit-password small-login validate form-control form-control-sm', 'placeholder':'Password', "autocomplete": "current-password"}))


def forms(request):
    return {"login_form": CustomAuthForm()}
