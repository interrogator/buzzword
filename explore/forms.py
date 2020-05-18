from django import forms
from .models import Corpus


class UploadCorpusForm(forms.ModelForm):
    class Meta:
        model = Corpus
        fields = ["name", "desc", "language", "date", "url"]

    corpus_file = forms.FileField()
