from django.db import models
from django.conf import settings
from django.contrib import admin, messages

from martor.widgets import AdminMartorWidget
from martor.models import MartorField

from explore.models import Corpus
from explorer.main import load_explorer_app
from .models import Post, OCRUpdate, PDF
from .utils import dump_latest




@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["commit_msg", "description"]
    formfield_overrides = {
        MartorField: {"widget": AdminMartorWidget},
        models.TextField: {"widget": AdminMartorWidget},
    }

@admin.register(OCRUpdate)
class OCRUpdateAdmin(admin.ModelAdmin):
    list_display = ["username", "accepted", "slug", "commit_msg", "timestamp", "previous", "text"]

    actions = ["accept_correction", "parse_latest"]

    def accept_correction(self, request, queryset):
        """
        https://docs.djangoproject.com/en/3.0/ref/contrib/admin/actions/
        """
        queryset.update(accepted=True)
        msg = f"{len(queryset)} changes accepted."
        self.message_user(request, msg, messages.SUCCESS)

    def parse_latest(self, request, queryset):
        """
        Todo one day, parse only the files that need it...
        """
        slug = settings.BUZZWORD_SPECIFIC_CORPUS
        slugs = {slug}
        
        for slug in slugs:
            num_parsed = dump_latest(slug=slug, parse=True)
            if not num_parsed:
                msg = "Nothing new to parse."
            else:
                msg = f"{num_parsed} files reparsed for {Corpus.objects.get(slug=slug).name}"
                self.message_user(request, msg, messages.SUCCESS)
            load_explorer_app(force=True)


    accept_correction.short_description = "Accept OCR update"
    parse_latest.short_description = "Parse latest accepted data (can take a few minutes)"


@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ["slug", "path", "name", "num"]





