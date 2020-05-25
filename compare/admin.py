from django.db import models
from django.contrib import admin

from martor.widgets import AdminMartorWidget
from martor.models import MartorField

from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ["commit_msg", "description"]
    formfield_overrides = {
        MartorField: {"widget": AdminMartorWidget},
        models.TextField: {"widget": AdminMartorWidget},
    }


admin.site.register(Post, PostAdmin)
