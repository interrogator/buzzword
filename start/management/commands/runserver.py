import os

import explorer.parts.main
from django.contrib.staticfiles.management.commands.runserver import \
    Command as RunServerCommand


class Command(RunServerCommand):

    def run(self, **options):
        if os.environ.get('RUN_MAIN', False):  # https://code.djangoproject.com/ticket/8085
            explorer.parts.main.load_corpora()
        super().run(**options)
