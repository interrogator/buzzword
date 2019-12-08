from django.contrib import admin
from explore.models import Corpus


@admin.register(Corpus)
class CorpusAdmin(admin.ModelAdmin):
    list_display = ('slug',)

    def get_fields(self, request, obj):
        if request.user.is_superuser: 
            return super().get_fields(request, obj)
        else: # staff
            return ['disabled', 'desc', 'name']

