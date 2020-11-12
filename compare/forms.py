from django import forms

from .models import Post
from django.forms.widgets import TextInput

class SubmitForm(forms.Form):
    description = forms.CharField()
    commit_msg = forms.CharField()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"

    commit_msg = forms.CharField(widget=TextInput(attrs={'class': 'form-control', "style": "min-width: 270px;"}))
