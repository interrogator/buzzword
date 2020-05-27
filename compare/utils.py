"""
Random utilities this app needs
"""
import os

from buzz import Corpus as BuzzCorpus
from explore.models import Corpus
from .models import OCRUpdate, PDF

# from django.core.exceptions import ObjectDoesNotExist


def markdown_to_buzz_input(markdown):
    """
    todo

    User can use markdown when correcting OCR
    We need to parse out headers and bulletpoints into <meta> features,
    handle italics and that sort of thing...perhaps we can convert the text
    to html and then postprocess that...
    """
    return markdown


def _get_tif_paths(slug):
    """
    Get sorted list of all TIF files in the slug's static dir
    """
    tifs_path = os.path.join("static", "tifs", slug + "-tifs")
    fs = os.listdir(tifs_path)
    tifs = [os.path.join(tifs_path, i) for i in fs if i.endswith(".tif")]
    return list(sorted(tifs))


def store_buzz_raw(raw, slug, pdf_path, corpus_path=None):
    """
    Put the raw text into the right place for eventual parsing
    """
    # todo: should it go into static?
    base = f"uploads/{slug}"
    os.makedirs(base, exist_ok=True)
    filename = os.path.basename(pdf_path).replace(".pdf", ".txt")
    with open(os.path.join(base, filename), "w") as fo:
        fo.write(raw)
    return base


def dump_latest():
    """
    Get the latest OCR corrections and build a parseable corpus.
    Maybe even parse it?
    """
    slugs = OCRUpdate.objects.values_list("slug")
    slugs = set(slugs)
    for slug in slugs:
        corp = Corpus.objects.get(slug=slug)
        lang = corp.language.name
        # get the associated pdfs
        pdfs = PDF.objects.filter(slug=slug)
        for pdf in pdfs:
            updates = OCRUpdate.objects.filter(pdf=pdf, slug=slug)
            plaintext = updates.latest("timestamp").text
            corpus_path = store_buzz_raw(plaintext, slug, pdf.path)
        print(f"Parsing ({lang}): {corpus_path}")
        corp = BuzzCorpus(corpus_path)
        parsed = corp.parse(language=lang, multiprocess=1)
        corp.parsed = True
        corp.path = parsed.path
        corp.save()
        return parsed
