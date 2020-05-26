import os
from .utils import _get_tif_paths
from .models import PDF, OCRUpdate, TIF
from django.db import IntegrityError

import pyocr

from PIL import Image


def _get_ocr_engine(lang):
    tools = pyocr.get_available_tools()
    print("tools", tools)
    tool = tools[0]
    langs = tool.get_available_languages()
    print("Available languages: %s" % ", ".join(langs))
    lang = langs[0]
    return tool, "deu_frak2"


def load_tif_pdf_plaintext(corpus):
    paths = _get_tif_paths(corpus.slug)
    ocr_engine, lang_chosen = _get_ocr_engine(corpus.language.name)
    for i, path in enumerate(paths):
        name = os.path.basename(path)
        name = os.path.splitext(name)[0]
        image = Image.open(path)
        pdf_path = path.replace(".tif", ".pdf")
        image.save(pdf_path)
        pdf = PDF(name=name, num=i, path=pdf_path, slug=corpus.slug)
        tif = TIF(name=name, num=i, path=path, slug=corpus.slug)
        try:
            pdf.save()
            tif.save()
            print(f"Storing PDF/TIF in DB: {pdf.path}")
            plaintext = ocr_engine.image_to_string(
                Image.open(path),
                lang=lang_chosen,
                builder=pyocr.builders.TextBuilder(),
            )
            ocr = OCRUpdate(
                slug=corpus.slug, commit_msg="OCR result", text=plaintext, pdf=pdf
            )
            print(f"Storing OCR result in DB: {plaintext[:100]}...")
            ocr.save()
        except IntegrityError:
            print(f"Exists in DB: {pdf.path} /// {tif.path}")
