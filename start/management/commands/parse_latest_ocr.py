import os


from compare.utils import dump_latest
from explorer.main import _load_corpora

from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunServerCommand,
)
from django.conf import settings

class Command(RunServerCommand):
    def run(self, **options):
        print("Dumping and parsing latest OCR")
        #fullpath = os.path.abspath(settings.CORPORA_FILE)
        #_load_corpora(fullpath)
        dump_latest(parse=True)
