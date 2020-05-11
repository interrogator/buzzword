from django import forms
from markdownx.fields import MarkdownxFormField


class OCRResult(forms.Form):
    content = MarkdownxFormField()
