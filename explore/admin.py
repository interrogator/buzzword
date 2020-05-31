from django.contrib import admin
from explore.models import Corpus, Language
from guardian.admin import GuardedModelAdmin


def reparse_corpus(modeladmin, request, queryset):
    """
    todo: write what happens when admin accepts correction
    """
    pass

reparse_corpus.short_description = "Reparse this corpus"


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["short", "name"]


@admin.register(Corpus)
class CorpusAdmin(GuardedModelAdmin):
    list_display = ("slug",)
    actions = [reparse_corpus]

    def get_fields(self, request, obj):
        if request.user.is_superuser:
            return super().get_fields(request, obj)
        else:  # staff
            return ["disabled", "desc", "name"]
