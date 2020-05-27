import os
from .utils import _get_tif_paths, store_buzz_raw, _is_meaningful
from .models import PDF, OCRUpdate, TIF
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import pyocr

from PIL import Image


def _get_ocr_engine(lang):
    """
    todo: handle english and other spacy languages

    * add to tessdata
    * make a mapping of language names to tess models
    """
    tools = pyocr.get_available_tools()
    tool = tools[0]
    # langs = tool.get_available_languages()
    # lang = langs[0]
    return tool, "deu_frak2"


def load_tif_pdf_plaintext(corpus):
    """
    From TIF files, convert to PDF for display, and get OCR
    via pyocr/tesseract

    todo: configure multilingual support
    todo: save as little as possible here, as OCR is slow!

    """
    tif_paths = _get_tif_paths(corpus.slug)
    ocr_engine, lang_chosen = _get_ocr_engine(corpus.language.name)
    tot = len(tif_paths)
    for i, tif_path in enumerate(tif_paths):
        pdf_path = tif_path.replace(".tif", ".pdf")
        name = os.path.basename(tif_path)
        name = os.path.splitext(name)[0]
        # make pdf if need be
        if not os.path.isfile(pdf_path):
            image = Image.open(tif_path)
            image.save(pdf_path)

        PDF.objects.get(slug=corpus.slug, num=i)

        # todo: use get_or_create
        pdf, pdf_created = PDF.objects.get_or_create(
            name=name, num=i, path=pdf_path, slug=corpus.slug
        )
        tif, tif_created = TIF.objects.get_or_create(
            name=name, num=i, path=tif_path, slug=corpus.slug
        )

        try:
            pdf.save()
            tif.save()

            print(f"({i+1}/{tot}) Stored PDF/TIF in DB: {pdf.path}")

            # if there is already an OCRUpdate for this PDF, not much left to do
            try:
                OCRUpdate.objects.get(pdf=pdf)
                print(f"OCRUpdate already found for {tif.path}")
                continue
            except ObjectDoesNotExist:
                pass

            print(f"Doing OCR for {tif.path}")

            # there is no OCRUpdate for this code; therefore we build and save it
            plaintext = ocr_engine.image_to_string(
                Image.open(tif_path),
                lang=lang_chosen,
                builder=pyocr.builders.TextBuilder(),
            )
            if not _is_meaningful(plaintext):
                plaintext = '<meta blank="true"/>'
            ocr = OCRUpdate(
                slug=corpus.slug, commit_msg="OCR result", text=plaintext, pdf=pdf
            )
            print(f"Storing OCR result for {tif_path} in DB...")
            ocr.save()
            # store the result as buzz plaintext corpus for parsing
            store_buzz_raw(plaintext, corpus.slug, pdf_path)
        except IntegrityError:
            print(f"Exists in DB: {pdf.path} /// {tif.path}")
