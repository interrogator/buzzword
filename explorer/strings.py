"""
buzzword explorer: making human-readable strings from data
"""
import json
import urllib.parse

from buzz.constants import SHORT_TO_LONG_NAME
from .lang import LANGUAGES


def _make_description(names, size):
    """
    Describe a user-uploaded corpus
    """
    desc = "User-uploaded data, {}. {} file{}: {}"
    form_names = ", ".join(names[:3])
    if len(names) > 3:
        form_names += "..."
    plu = "s" if len(names) != 1 else ""
    return desc.format(_format_size(size), len(names), plu, form_names)


def _make_table_name(specs=None, search_from=None, show=None, subcorpora=None, relative=None, keyness=None, sort=None, **kwargs):
    """
    Generate a table name from its history
    """
    if not show and not subcorpora:
        return "Part of speech tags by filename"

    multi = False
    cont = False
    if subcorpora is None:
        subcorpora = "corpus"
    subcorpora = (
        SHORT_TO_LONG_NAME.get(subcorpora, subcorpora).lower().replace("_", " ")
    )
    show = [SHORT_TO_LONG_NAME.get(i, i).lower().replace("_", " ") for i in show]
    show = "+".join(show)
    relkey = ", rel. freq." if relative else ", keyness"
    if keyness:
        relkey = f"{relkey} ({keyness})"
    if relative is False and keyness is False:
        relkey = " showing absolute frequencies"
    basic = f"{show} by {subcorpora}{relkey}, sorting by {sort}"
    if len(show) > 1 and multi:
        basic += " (columns split)"
    if not int(search_from):  # todo: fix
        return basic
    return f"{basic} -- from search #{search_from}"


def _format_size(size):
    """
    Format size in bytes, kb, or mb
    """
    if size < 1000:
        return f"{size} bytes"
    if size >= 1000000:
        return f"{size/1000000:.2f} MB"
    if size >= 1000:
        return f"{size/1000:.2f} kB"


def _make_search_name(search_result, size, lang):
    """
    Generate a search name from its history
    """
    from explore.models import SearchResult
    trans = {0: "match", 1: "bigrams", 2: "trigrams"}
    if isinstance(search_result, str):
        searchlang = LANGUAGES[("search-default", None)][int(lang)]
        return f"{searchlang} {search_result} ({size} tokens)"
    skip = search_result.inverse
    search_string = search_result.query
    n = search_result.idx
    n_results = len(json.loads(search_result.indices))
    gram = 0  # swisslaw
    no = "not " if skip else ""
    col = SHORT_TO_LONG_NAME.get(search_result.target, search_result.target)
    relative_corpus = n_results * 100 / size  # list / int
    parent = getattr(search_result, "parent", None)
    if parent is None:
        prev_total = None
    else:
        prev_total = parent.indices.count(",") + 1
    rel_last = ""
    if prev_total is not None:
        rel_last = n_results * 100 / prev_total
        rel_last = f"/{rel_last:.2f}%"
    freq = f"(n={n_results:n}{rel_last}/{relative_corpus:.2f}%)"
    show = " " if not gram else f"(showing {trans[gram]}) "
    basic = f"{col} {no}matching '{search_string}' {show}{freq}"
    hyphen = ""
    while parent is not None:
        hyphen += "──"
        parent = parent.parent
    if hyphen:
        basic = f"└{hyphen} " + basic
    return f"({n}) {basic}"


def _search_error(col, search_string):
    """
    Check for problems with search
    """
    if not search_string:
        return "No search string provided."
    if not col:
        return "No feature selected to search."
    return ""


def _table_error(show, subcorpora, updating):
    """
    Check for problems with table
    """
    if updating:
        return ""
    errors = []
    if not show:
        errors.append("No choice made for feature to use as columns.")
    # this is now allowed ... can probably remove this function if
    # we don't do any extra validations.
    if not subcorpora:
        errors.append("No choice made for feature to use as index.")
    if not errors:
        return ""
    plural = "s" if len(errors) > 1 else ""
    return f"Error{plural}\n* " + "\n* ".join(errors)


def _capitalize_first(s):
    """
    First letter capitalised and notheing else
    """
    return s[0].upper() + s[1:]


def _downloadable_name(name):
    """
    Make a safe filename for CSV download. todo: url safe?
    """
    name = name.lower().split("-- from ")[0]
    name = name.replace(" ", "-")
    ok = {"-", "_"}
    name = "".join([i for i in name if i.isalnum() or i in ok])
    return name.strip("- ").lower()


def _slug_from_name(name):
    """
    Make a slug from an (uploaded) corpus name
    """
    name = name.replace(" ", "-").lower()
    return urllib.parse.quote_plus(name)
