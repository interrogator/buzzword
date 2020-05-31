from django.db import models
from django.contrib import admin

from martor.widgets import AdminMartorWidget
from martor.models import MartorField

from .models import Post, OCRUpdate, PDF




@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["commit_msg", "description"]
    formfield_overrides = {
        MartorField: {"widget": AdminMartorWidget},
        models.TextField: {"widget": AdminMartorWidget},
    }

@admin.register(OCRUpdate)
class OCRUpdateAdmin(admin.ModelAdmin):
    list_display = ["slug", "commit_msg", "timestamp", "previous", "text"]
    formfield_overrides = {
        MartorField: {"widget": AdminMartorWidget},
        models.TextField: {"widget": AdminMartorWidget},
    }

    actions = ['accept_correction']

    def accept_correction(self, request, queryset):
        """
        todo: write what happens when admin accepts correction
        """
        msg = f"{len(queryset)} changes accepted."
        self.message_user(request, msg, messages.SUCCESS)

    accept_correction.short_description = "Accept OCR update"

@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ["slug", "path", "name", "num"]




