"""
Random utilities this app needs
"""
import os
import re

from buzz import Corpus as BuzzCorpus
from buzz import Collection
from django.conf import settings

from explore.models import Corpus
from .models import OCRUpdate, PDF


# from django.core.exceptions import ObjectDoesNotExist

# when doing OCR, re.findall will be run on it using this regex, which sort of
# approximates a word. note that this will mean that "the end" will be marked
# as blank, but that is a decent tradeoff for marking blank a lot of junk pages.
MEANINGFUL = r"[A-Za-z]{3,}"
THRESHOLD = 3


def markdown_to_buzz_input(markdown, slug):
    """
    todo

    User can use markdown when correcting OCR
    We need to parse out headers and bulletpoints into <meta> features,
    handle italics and that sort of thing...perhaps we can convert the text
    to html and then postprocess that...
    """
    fixed = []
    lines = markdown.splitlines()
    for line in lines:
        # handle headings
        # note that this doesn't put text inside respective headings as sections.
        # doing so would not work across pages anyway.
        if line.startswith("#"):
            pref, head = line.split(" ", 1)
            depth = len(pref.strip())
            head = head.strip()
            line = f"<meta heading=\"true\" depth=\"{depth}\">{head}</meta>"
        # handle bulletpoints
        elif line.startswith("* "):
            line = line.lstrip("* ")
            line = "<meta point=\"true\">{line}</meta>"
        for styler in ["***", "**", "*", "`"]:
            pass
        fixed.append(line)
    return "\n".join(fixed)

def store_buzz_raw(raw, slug, pdf_path):
    """
    Put the raw text into the right place for eventual parsing
    """
    # todo: corpora dir?
    base = os.path.join("static", "corpora", slug, "txt")
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


def _is_meaningful(plaintext, language):
    """
    Determine if an OCR page contains something worthwhile
    """
    # skip this check for non latin alphabet ... right now the parser doesn't
    # accept most non-latin languages, so it's mostly academic for now...
    if lang in {"zh", "ja", "fa", "iw", "ar"}:
        return True
    words = re.findall(plaintext, MEANINGFUL)
    return len(words) >= THRESHOLD


def _handle_page_numbers(text):
    """
    Attempt to make page-level metadata containing page number
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

    page_number = None
    ix_to_delete = set()

    # lines is just the first and last, stripped
    for i, line in enumerate(lines):
        if line.isnumeric():
            page_number = line
            ix_to_delete.add(i)
            break

    if page_number is not None:
        form = f"<meta page={page_number} />\n"

    # we also want to REMOVE page number from the actual text
    cut = [x for i, x in enumerate(text.splitlines()) if i not in ix_to_delete]
    if form:
        cut = [form] + cut
    return "\n".join(cut)
