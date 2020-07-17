from django import forms
from django.forms.widgets import PasswordInput, TextInput

from django.contrib.auth.forms import AuthenticationForm


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'validate form-control form-control-sm','placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class':'validate form-control form-control-sm', 'placeholder':'Password'}))


def forms(request):
    return {"login_form": CustomAuthForm()}
