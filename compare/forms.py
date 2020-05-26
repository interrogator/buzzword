from django import forms

from martor.fields import MartorFormField
from .models import Post


class SubmitForm(forms.Form):
    description = forms.CharField()
    commit_msg = forms.CharField(widget=forms.TextInput())


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
