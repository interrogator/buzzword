"""
Random utilities this app needs
"""
import os
import re

from buzz import Corpus as BuzzCorpus
from django.conf import settings

from explore.models import Corpus
from .models import OCRUpdate, PDF


# from django.core.exceptions import ObjectDoesNotExist

# there needs to be at least 3 occurrences of this pattern for a text to not be junk
MEANINGFUL = r"[A-Za-z0-9]{3}"
THRESHOLD = 3


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


def _is_meaningful(plaintext):
    """
    Determine if an OCR page contains something worthwhile
    """
    found = re.findall(MEANINGFUL, plaintext)
    return len(found) >= THRESHOLD


def _handle_page_numbers(text):
    """
    Attempt to make page-level metadata containing page and header
    """
    # if no handling, just return text
    if settings.COMPARE_HANDLE_PAGE_NUMBERS is False:
        return text
    # get first and maybe last line as list
    lines = [i.strip() for i in text.splitlines() if i.strip()]
    if not lines:
        return text
    if len(lines) == 1:
        lines = [lines[0]]
    else:
        lines = [lines[0], lines[-1]]

    # if we find page_number, it goes here
    page_number = None
    # page number lines to remove if set to remove
    ix_to_delete = set()
    # if we find a header beside the page number it goes here
    header = ""
    # lines is just the first and last, stripped
    for i, line in enumerate(lines):
        # if it's numerical, we found it. either store for deletion
        # or remember it as page_number
        if line.isnumeric():
            if settings.COMPARE_HANDLE_PAGE_NUMBERS is None:
                ix_to_delete.add(i)
                continue
            else:
                page_number = line
                ix_to_delete.add(i)
                break
        # maybe there's a header printbeside the page number
        sublines = [(ii, n) for ii, n in enumerate(line.split())]
        for ix, part in sublines:
            # if there is a numerical part in the page numbering,
            if part.strip().isnumeric():
                # then get that from the sublist
                page_number = sublines.pop(ix)[1].strip()
                ix_to_delete.add(i)
                break
        # if we're on header, not footer, we may have a header!
        if not i:
            header = " ".join([x[-1] for x in sublines])
            header = header.replace("'", "").replace('"', "")
            header = "".join([x for x in header if x.isalnum() or x.isspace()])
            if not header.strip():
                header = None
            else:
                ix_to_delete.add(i)
        # footer via: elif i == 1: ...

    # build header if we have it
    if header:
        header = f'header="{header.strip()}" '

    # settings todo: right now you only get header detection if page detection
    # and if page number found!
    form = None
    if page_number is not None and settings.COMPARE_HANDLE_PAGE_NUMBERS:
        form = f"<meta {header}page={page_number} />\n"
    elif header and page_number is None and settings.COMPARE_HANDLE_PAGE_NUMBERS:
        form = f"<meta {header}/>\n"

    # if we want the page numbers REMOVED
    cut = [x for i, x in enumerate(text.splitlines()) if i not in ix_to_delete]
    if form:
        cut = [form] + cut
    return "\n".join(cut)
