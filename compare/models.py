from django.db import models
from markdownx.models import MarkdownxField


class OCRText(models.Model):
    content = MarkdownxField()
    commit_msg = models.TextField(blank=True)
