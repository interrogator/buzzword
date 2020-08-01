import os
from explore.models import Corpus
from explorer.main import _load_languages, _load_corpora
from compare.load import load_tif_pdf_plaintext

from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunServerCommand,
)
from django.conf import settings
import sys

class Command(RunServerCommand):
    def run(self, **options):
        _load_languages()
        _load_corpora()
        slug = sys.argv[-1] if sys.argv[-1] != "do_ocr" else False
        for corpus in Corpus.objects.all():
            if not corpus.pdfs:
                continue
            if corpus.disabled:
                continue
            if slug and corpus.slug != slug:
                continue
            os.environ["TESSDATA_PREFIX"] = settings.TESSDATA_PREFIX
            load_tif_pdf_plaintext(corpus)