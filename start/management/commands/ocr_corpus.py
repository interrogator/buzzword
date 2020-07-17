import os

from compare.utils import dump_latest
from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunServerCommand,
)


class Command(RunServerCommand):
    def run(self, **options):
        print("Dumping latest OCR")
        dump_latest()
