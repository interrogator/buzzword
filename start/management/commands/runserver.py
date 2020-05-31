import os

from explorer.parts.main import load_explorer_app
from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunServerCommand,
)


class Command(RunServerCommand):
    def run(self, **options):
        """
        see https://code.djangoproject.com/ticket/8085
        """
        if os.environ.get("RUN_MAIN", False):
            load_explorer_app()
        super().run(**options)
