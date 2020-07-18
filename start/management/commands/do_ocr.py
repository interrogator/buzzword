import os
from explore.models import Corpus
from explorer.main import _load_languages, _load_corpora
from compare.load import load_tif_pdf_plaintext

from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunServerCommand,
)
from django.conf import settings


class Command(RunServerCommand):
    def run(self, **options):
        fullpath = os.path.abspath(settings.CORPORA_FILE)
        print(f"Using corpus configuration at: {fullpath}")
        _load_languages()
        _load_corpora(fullpath)
        for corpus in Corpus.objects.all():
            if corpus.pdfs and not corpus.disabled:
                os.environ["TESSDATA_PREFIX"] = settings.TESSDATA_PREFIX
                load_tif_pdf_plaintext(corpus)