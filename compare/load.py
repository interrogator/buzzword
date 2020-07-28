import os
from .utils import store_buzz_raw, _is_meaningful, _handle_page_numbers, _remove_junk
from .models import PDF, OCRUpdate, TIF
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import pyocr
import pytesseract
from pytesseract import Output

from PIL import Image

from buzz import Collection


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
    collection = Collection(corpus.path)
    ocr_engine, lang_chosen = _get_ocr_engine(corpus.language.name)
    tot = len(collection.tiff.files)
    for i, tif_file in enumerate(collection.tiff.files):
        tif_path = tif_file.path
        pdf_path = tif_path.replace('/tiff/', "/pdf/").replace("/tif/", "/pdf/").replace(".tif", ".pdf")
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        name = os.path.basename(tif_path)
        name = os.path.splitext(name)[0]
        # make pdf if need be
        if not os.path.isfile(pdf_path):
            image = Image.open(tif_path)
            image.save(pdf_path)

        # todo: use get_or_create
        pdf, pdf_created = PDF.objects.get_or_create(
            name=name, num=i, path=pdf_path, slug=corpus.slug
        )
        tif, tif_created = TIF.objects.get_or_create(
            name=name, num=i, path=tif_path, slug=corpus.slug
        )

        if pdf_created:
            pdf.save()
        if tif_created:
            tif.save()

        if pdf_created or tif_created:
            print(f"({i+1}/{tot}) Stored PDF/TIF in DB: {pdf.path}")
        if not pdf_created and not tif_created:
            print(f"Exists in DB: {pdf.path} /// {tif.path}")

        # if there is already an OCRUpdate for this PDF, not much left to do
        # todo: fallback to preprocessed/txt ?? otherwise every reload causes
        # ocr to happen
        ocrs = OCRUpdate.objects.filter(pdf=pdf)
        if ocrs:
            continue

        # if there are text files for this corpus
        # and there are more or same amount as the tifs,
        # get the text data and save as OCR result
        if collection.txt and len(collection.txt.files) >= tot:
            path = collection.txt.files[i].path
            print(f"Text file exists at {path}; skipping OCR")
            with open(path, "r") as fo:
                plaintext = fo.read()
            ocr = OCRUpdate(
                slug=corpus.slug, commit_msg="OCR result", text=plaintext, pdf=pdf, accepted=True
            )
            ocr.save()
        else:
            print(f"Doing OCR for {tif.path}")

            # there is no OCRUpdate for this data; therefore we do OCR and save it
            plaintext = ocr_engine.image_to_string(
                Image.open(tif_path),
                lang=lang_chosen,
                builder=pyocr.builders.TextBuilder(),
            )
            # this block would add meta coordinates to each word.
            # the problem is, we can't load this text into the editor. and,
            # if we strip out the tags, then when the user saves the data,
            # we lose all the tags. so i can't see any way around this...
            if False:
                try:
                    d = pytesseract.image_to_data(Image.open(tif_path), output_type=Output.DICT, lang="deu_frak2")
                except:  # no text at all
                    d = {}

                n_boxes = len(d.get('level', []))

                text_out = []
                for i in range(n_boxes):
                    text = d['text'][i]
                    if not text:
                        text = "\n"
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    if text != "\n":
                        text = f"<meta x=\"{x}\" y=\"{y}\" w=\"{w}\" h=\"{h}\" >{text}</meta>"
                    # d['conf'][i] == certainty
                    text_out.append(text)
                plaintext = "\n".join([i.strip(" ") for i in " ".join(text_out).splitlines()])

            plaintext = _handle_page_numbers(plaintext, tif_path)

            if not _is_meaningful(plaintext, corpus.language.short):
                plaintext = '<meta blank="true"/>'

            plaintext = _remove_junk(plaintext, corpus.language.short)

            ocr, ocr_created = OCRUpdate.objects.get_or_create(
                slug=corpus.slug, commit_msg="OCR result", text=plaintext, pdf=pdf, accepted=True
            )
            if ocr_created:
                print(f"Stored OCR result for {tif_path} in DB...")
            else:
                print(f"OCR already exists in DB for: {tif_path}")

            # store the result as buzz plaintext corpus for parsing
            store_buzz_raw(plaintext, corpus.slug, pdf_path)
