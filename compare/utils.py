"""
Random utilities this app needs
"""
import os

from explore.models import Corpus


def markdown_to_buzz_input(markdown):
    """
    User can use markdown when correcting OCR
    We need to parse out headers and bulletpoints into <meta> features
    """
    return markdown


def filepath_for_pdf(pdf):
    return f"PATH TO {pdf}"


def get_raw_text_for_ocr(slug, pdf_file):
    corpus = Corpus.objects.get(slug=slug)  # not needed?
    # corpath = corpus.path.rsplit("-parsed")[0]
    corpath = os.path.join("static", "plaintexts", slug)
    text_version = os.path.basename(pdf_file.replace(".pdf", ".txt"))
    corfile = os.path.join(corpath, text_version)
    print("GETTING PLAINTEXT", slug, pdf_file, corpath, corfile)
    with open(corfile, "r") as fo:
        data = fo.read()
    return data
