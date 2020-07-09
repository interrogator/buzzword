import os

import explorer.parts.main
from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunServerCommand,
)


class Command(RunServerCommand):
    def run(self, **options):
        # https://code.djangoproject.com/ticket/8085
        explorer.parts.main.load_corpora()
