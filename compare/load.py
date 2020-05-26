import os
from .utils import _get_pdf_paths
from .models import PDF
from django.db import IntegrityError


def load_pdfs(corpus):
    paths = _get_pdf_paths(corpus.slug)
    for i, path in enumerate(paths):
        name = os.path.basename(path)
        name = os.path.splitext(name)[0]
        pdf = PDF(name=name, num=i, path=path, slug=corpus.slug)
        try:
            pdf.save()
            print(f"Storing PDF in DB: {pdf.path}")
        except IntegrityError:
            print(f"PDF exists in DB: {pdf.path}")
