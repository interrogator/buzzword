import os

from compare.utils import dump_latest
from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunServerCommand,
)


class Command(RunServerCommand):
    def run(self, **options):
        if os.environ.get(
            "RUN_MAIN", False
        ):  # https://code.djangoproject.com/ticket/8085
            compare.utils.dump_latest()
        super().run(**options)
