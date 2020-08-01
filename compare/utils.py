"""
Random utilities this app needs
"""
import os
import re
import shutil

from buzz import Collection
from django.conf import settings

from explore.models import Corpus
from .models import OCRUpdate, PDF


# from django.core.exceptions import ObjectDoesNotExist

# when doing OCR, re.findall will be run on it using this regex, which sort of
# approximates a word. note that this will mean that "the end" will be marked
# as blank, but that is a decent tradeoff for marking blank a lot of junk pages.
MEANINGFUL = "[A-Za-z]{3,}"
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


def _unwrap(text):
    """
    Change the txt from how it should appear on-screen (i.e. with word-breaks)
    to how it is best parsed
    """
    # remove trailing space
    text = "\n".join([i.strip() for i in text.splitlines()])
    # unwrap words
    text = re.sub("[-–—]\s*\n\s*", "", text)
    # replace more than two spaces with one
    text = re.sub(r" {2,}", " ", text)
    # replace newline with space (so two newlines == two spaces)
    text = text.replace("\n", " ")
    # replace two or more spaces (from the newlines) with \n\n
    text = re.sub(" {2,}", "\n\n", text)
    # fix initial metadata
    text = text.replace("/> ", "/>\n", 1)
    # return with one newline at end
    return text.strip() + "\n"


def store_buzz_raw(raw, slug, pdf_path, unwordwrap=False):
    """
    Put the raw text into the right place for eventual parsing
    """
    if unwordwrap:
        raw = _unwrap(raw)

    base = os.path.join("static", "corpora", slug, "txt")
    os.makedirs(base, exist_ok=True)
    filename = os.path.basename(pdf_path).replace(".pdf", ".txt")
    outpath = os.path.join(base, filename)
    print(f"Saving txt: {outpath}")
    with open(outpath, "w") as fo:
        fo.write(raw)
    return outpath


def dump_latest(parse=False, slug=None):
    """
    Get the latest OCR corrections and build a parseable corpus

    Optionally, parse it
    """
    slugs = {slug} if slug else set(OCRUpdate.objects.values_list("slug"))
    for slug in slugs:
        print(f"Storing latest and parsing: {slug}")
        if isinstance(slug, tuple):
            slug = slug[0]  # the set is a weird tuple thing
        corp = Corpus.objects.get(slug=slug)
        if not corp.pdfs:
            continue
        lang = corp.language.short
        # get the associated pdfs
        pdfs = PDF.objects.filter(slug=slug)
        to_be_parsed = set()
        old_versions = set()
        for pdf in pdfs:
            updates = OCRUpdate.objects.filter(pdf=pdf, slug=slug, accepted=True)
            if not updates:
                msg = f"No accepted OCR for {pdf.path}. Something is very wrong."
                print(msg)
                raise ValueError(msg)
            # get latest accepted
            latest = updates.latest("timestamp")
            if latest.currently_parsed:
                print(f"Latest version of {pdf.path} OCR is already parsed")
            else:
                store_buzz_raw(latest.text, slug, pdf.path, unwordwrap=True)
                to_be_parsed.add(latest)
            all_versions = OCRUpdate.objects.filter(pdf=pdf, slug=slug)
            for version in all_versions:
                if version != latest:
                    old_versions.add(version)
        if parse:
            parsed_dir = os.path.expanduser(os.path.join(corp.path, "conllu"))
            # now delete the conllu files that need to be reparsed
            if not len(to_be_parsed):
                print("Nothing to parse!")
                return
            print(f"Parsing {len(to_be_parsed)} files for {slug}...")
            for ocr_update in to_be_parsed:
                filename = ocr_update.pdf.name + ".conllu"
                filepath = os.path.join(parsed_dir, filename)
                if os.path.isfile(filepath):
                    print(f"Deleting {filepath} so we can reparse it...")
                    os.remove(filepath)
            coll = Collection(corp.path)
            print(f"Parsing ({lang}): {corp.path}")
            parsed = coll.parse(language=lang, multiprocess=False, just_missing=True)
            corp.parsed = True
            corp.save()
            # now store info about which update is currently parsed
            for update in to_be_parsed:
                update.currently_parsed = True
                update.save()
            for old_version in old_versions:
                old_version.currently_parsed = False
                old_version.save()
            return len(to_be_parsed)


def _is_meaningful(plaintext, language):
    """
    Determine if an OCR page contains something worthwhile
    """
    # skip this check for non latin alphabet ... right now the parser doesn't
    # accept most non-latin languages, so it's mostly academic for now...
    if language in {"zh", "ja", "fa", "iw", "ar"}:
        return True
    words = re.findall(MEANINGFUL, plaintext)
    return len(words) >= THRESHOLD


def _remove_junk(plaintext, language):
    """
    """
    if language in {"zh", "ja", "fa", "iw", "ar"}:
        return plaintext
    lines = plaintext.splitlines()
    lines = [l for l in lines if re.findall(MEANINGFUL, l) or not l.strip() or l.startswith("<meta")]
    out = "\n".join(lines).strip() + "\n"
    out = re.sub("\n{2,}", "\n\n", out)
    return out


def _handle_page_numbers(text, filename):
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

    # todo: this is swisslaw only
    if "1803" in filename:
        year = "1803"
    elif "1847" in filename:
        year = "1847"
    elif "CF_650" in filename:
        year = "1887"
    else:
        year = "unknown"

    form = False
    if page_number is not None:
        form = f"<meta year=\"{year}\" page=\"{page_number}\" />\n"
    else:
        form = f"<meta year=\"{year}\" />"


    # we also want to REMOVE page number from the actual text
    cut = [x for i, x in enumerate(text.splitlines()) if i not in ix_to_delete]
    if form:
        cut = [form] + cut
    return "\n".join(cut)
