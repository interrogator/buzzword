from django.contrib import admin
from explore.models import Corpus
from guardian.admin import GuardedModelAdmin


@admin.register(Corpus)
class CorpusAdmin(GuardedModelAdmin):
    list_display = ("slug",)

    def get_fields(self, request, obj):
        if request.user.is_superuser:
            return super().get_fields(request, obj)
        else:  # staff
            return ["disabled", "desc", "name"]
