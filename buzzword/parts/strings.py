"""
buzzword: making human-readable strings from data
"""

from buzz.constants import SHORT_TO_LONG_NAME


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


def _make_table_name(history):
    """
    Generate a table name from its history
    """
    if history == "initial":
        return "Part of speech tags by filename"
    specs, show, subcorpora, relative, keyness, sort, n, updates = history
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
    if updates:
        basic += f", {updates} edits"
    parent = specs[-2] if isinstance(specs, (tuple, list)) else 0
    if not parent:
        return basic
    return f"{basic} -- from search #{parent}"


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


def _make_search_name(history, size):
    """
    Generate a search name from its history
    """
    import locale

    locale.setlocale(locale.LC_ALL, "")
    if isinstance(history, str):
        return f"Search entire corpus: {history} ({size:n} tokens)"
    previous, col, skip, search_string, n, n_results, _ = history
    no = "not " if skip else ""
    col = SHORT_TO_LONG_NAME.get(col, col)
    relative_corpus = n_results * 100 / size
    prev_total = previous[-1] if isinstance(previous, (tuple, list)) else None
    rel_last = ""
    if prev_total is not None:
        rel_last = n_results * 100 / prev_total
        rel_last = f"/{rel_last:.2f}%"
    freq = f"(n={n_results:n}{rel_last}/{relative_corpus:.2f}%)"
    basic = f"{col} {no}matching '{search_string}' {freq}"
    hyphen = ""
    while isinstance(previous, (tuple, list)):
        hyphen += "──"
        previous = previous[0]
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
    if not subcorpora:
        errors.append("No choice made for feature to use as index")
    if not errors:
        return ""
    return "* " + "\n* ".join(errors)


def _capitalize_first(s):
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
    for repl in ["/", ".", " "]:
        name = name.replace(repl, "-")
    return name.lower()
