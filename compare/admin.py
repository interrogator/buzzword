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
    list_display = ["username", "user", "accepted", "slug", "commit_msg", "timestamp", "previous", "text"]
    #formfield_overrides = {
    #    MartorField: {"widget": AdminMartorWidget},
    #    models.TextField: {"widget": AdminMartorWidget},
    #}

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
        msg = f"'{Corpus.objects.get(slug=slug).name}' reparsed."
        for slug in slugs:
            parsed = dump_latest(slug=slug, parse=True)
            if not parsed:
                msg = "Nothing new to parse."
            #_get_or_load_corpora(slug=slug, force=True)
            load_explorer_app(force=True)
        self.message_user(request, msg, messages.SUCCESS)


    accept_correction.short_description = "Accept OCR update"
    parse_latest.short_description = "Parse latest accepted data (can take a few minutes)"


@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ["slug", "path", "name", "num"]





