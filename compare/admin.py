from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import OCRText

admin.site.register(OCRText, MarkdownxModelAdmin)
