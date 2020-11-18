"""
buzzword explorer: helpers and utilities
"""

import json
import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd
from buzz.constants import SHORT_TO_COL_NAME, SHORT_TO_LONG_NAME
from buzz.corpus import Corpus

from .strings import _capitalize_first, _downloadable_name
from buzzword.utils import management_handling


def _get_specs_and_corpus(search_from, searches, corpora, slug):
    """
    Get the correct corpus based on search_from
    """
    # if the user wants the corpus, return that
    if not int(search_from):
        return 0, _get_corpus(slug)
    # otherwise, get the search result (i.e. _n col) and make corpus
    exists = searches[str(search_from)]
    return int(search_from), _get_corpus(slug).iloc[exists[-1]]


def _tuple_or_list(this_identifier, typ):
    """
    Turn all lists to tuple/list so this becomes hashable/dcc.storable
    """
    opposite = tuple if typ == list else list
    out = []
    for i in this_identifier:
        if isinstance(i, opposite):
            i = _tuple_or_list(i, typ)
            out.append(typ(i))
        else:
            out.append(i)
    return typ(out)


def _translate_relative(inp):
    """
    Get relative and keyness from two-character input
    """
    if not inp:
        return False, False
    mapping = dict(t=True, f=False, n="corpus", l="ll", p="pd")  # noqa: E741
    return mapping[inp[0]], mapping[inp[1]]


def _drop_cols_for_datatable(df, add_governor):
    """
    For CONLL table, remove columns that we don't want:

    - parse, text, etc
    - underscored
    - governor attributes if loaded
    """
    if not isinstance(df, pd.DataFrame):
        return df
    drops = ["parse", "text", "e", "sent_id", "sent_len"]
    drops += [i for i in df.columns if i.startswith("_")]
    if add_governor:
        drops += ["gw", "gl", "gp", "gx", "gf", "gg"]
    drops = [i for i in drops if i in df.columns]
    return df.drop(drops, axis=1)


def _get_cols(corpus, add_governor):
    """
    Make list of dicts of conll columns (for search/show) in good order

    Do it by hand because we want a particular order (most common for search/show)
    """
    # normal good features to show
    col_order = ["w", "l", "p", "x", "f", "g", "file", "s", "i"]
    # speaker is kind of privileged by convention
    is_df = isinstance(corpus, pd.DataFrame)
    index_names = list(corpus.index.names) if is_df else ["file", "s", "i"]
    columns = list(corpus.columns) if is_df else list(corpus.files[0].load().columns)

    if "speaker" in columns:
        col_order.append("speaker")
    # next is all the governor bits if loaded
    if add_governor:
        col_order += ["gw", "gl", "gp", "gx", "gf", "gg"]
    # never show underscored, and never show parse, text, etc.
    under = [i for i in columns if i.startswith("_")]
    noshow = ["e", "o", "text", "sent_len", "sent_id", "parse"] + under
    # get only items that are actually in dataset
    possible = index_names + columns
    # add anything in dataset not already added (i.e. random metadata)
    col_order += [i for i in possible if i not in col_order + noshow]
    # do the formatting of name and id and return it
    longs = [
        (i, _capitalize_first(SHORT_TO_LONG_NAME.get(i, i)).replace("_", " "))
        for i in col_order
        if i in possible
    ]
    return [dict(value=v, label=l) for v, l in longs]


def _update_frequencies(df, deletable, content_table):
    """
    Turn DF into dash table data for frequencies
    """
    multicols = isinstance(df.columns, pd.MultiIndex)
    names = ["_" + str(x) for x in df.index.names]
    df.index.names = names

    if not multicols:
        columns = [
            {
                "name": i.lstrip("_"),
                "id": i,
                "deletable": deletable and "_" + i not in names,
                "hideable": True,
                "presentation": ("markdown" if i == "file" else None)

            }
            for i in df.columns
        ]
        return columns, df.to_dict("rows")

    columns = [
        {
            "name": [x.strip("_") for x in i],
            "id": "-".join(i),
            "deletable": ["_" + x in names for x in i],
            "hideable": True,
            "presentation": ("markdown" if i == "file" else None)
        }
        for i in df.columns
    ]
    # format multiindex column data correctly (by id)
    rows = []
    for row in df.to_dict("rows"):
        rows.append({"-".join(name): val for name, val in row.items()})
    return columns, rows


def _update_concordance(df, deletable):
    """
    Turn DF into dash table data for concordance
    """
    col_order = ["left", "match", "right", "file", "s", "i"]
    if "speaker" in df.columns:
        col_order.append("speaker")
    df = df[[i for i in col_order if i is not None]]
    cannot_delete = {"left", "match", "right"}
    columns = [
        {
            "name": _capitalize_first(SHORT_TO_COL_NAME.get(i, i)),
            "id": i,
            "deletable": i not in cannot_delete and deletable,
            "hideable": True,
            "presentation": ("markdown" if i == "match" else None)
        }
        for i in df.columns
    ]
    return columns, df.to_dict("rows")


def _update_conll(df, deletable, drop_govs, slug=None):
    """
    Turn DF into dash table data for conll
    """
    df = _drop_cols_for_datatable(df, drop_govs)
    col_order = ["file", "s", "i"] + list(df.columns)
    df = df.reset_index()
    # do not show file extension, todo: one expression
    df["file"] = df["file"].str.replace(".conllu", "", regex=False)
    df["file"] = df["file"].str.replace(f"^.*/conllu/", "", regex=True)
    df = _add_links(df, slug=slug, conc=False)
    df = df[[i for i in col_order if i is not None]]
    cannot_delete = {"s", "i"}
    columns = [
        {
            "name": _capitalize_first(SHORT_TO_COL_NAME.get(i, i)),
            "id": i,
            "deletable": i not in cannot_delete and deletable,
            "hideable": True,
            "presentation": ("markdown" if i == "file" else None)
        }
        for i in df.columns
    ]
    return columns, df.to_dict("rows")


def _postprocess_corpus(df, corpus_model):
    """
    Fix corpus if the user wants this on command line
    """
    if settings.MAX_DATASET_ROWS is not None:
        df = df.iloc[:settings.MAX_DATASET_ROWS, :]
    if corpus_model.drop_columns is not None:
        df = df.drop(corpus_model.drop_columns, axis=1, errors="ignore")
    return df


def _make_csv(table, long_name):
    """
    Save a CSV for table with this name
    """
    from .main import CONFIG

    fname = _downloadable_name(long_name)
    fpath = os.path.join(CONFIG["root"], f"csv/{fname}.csv")
    df = pd.DataFrame.from_dict(table)
    csv_string = df.to_csv(index=False, encoding="utf-8")
    with open(fpath, "w") as fo:
        fo.write(csv_string)
    return fpath


def _get_corpus(slug):
    """
    Get corpus from slug, loading from uploads dir if need be
    """
    from start.apps import corpora
    if slug in corpora:
        corpus = corpora[slug]
        return corpus
    raise ValueError(f"Corpus not found: {slug}")


def _cast_query(query, col):
    """
    ALlow different query types (e.g. numerical, list, str)
    """
    query = query.strip()
    if col in {"t", "d"}:
        return query
    if query.startswith("[") and query.endswith("]"):
        if "," in query:
            query = ",".split(query[1:-1])
            return [i.strip() for i in query]
    if query.isdigit():
        return int(query)
    try:
        return float(query)
    except Exception:
        return query


def register_callbacks():
    """
    Control when callbacks get registered
    """
    from . import callbacks  # noqa: F401


def _get_corpora_json_contents(corpora_file):
    """
    Get the contents of corpora.json, or an empty dict
    """
    exists = os.path.isfile(corpora_file)
    if not exists:
        print("Corpora file not found at {}!".format(corpora_file))
        return dict()
    with open(corpora_file, "r") as fo:
        return json.loads(fo.read())


def _special_search(df, col, search_string, skip, multiword):
    """
    Perform nonstandard search types (tgrep, depgrep, describe)

    todo: proper error handling etc
    """
    mapped = dict(t="tgrep", d="depgrep", describe="describe")
    try:
        # note, describe inverse is nonfunctional!
        matches = getattr(df, mapped[col])(search_string, inverse=skip, multiword=multiword)
        if matches is None or not len(matches):
            return None, "No results found, sorry."
        return matches, None
    except Exception as error:
        msg = f"search error for {col} ({search_string}): {type(error)}: {error}"
        print(msg)
        return df.iloc[:0, :0], msg

def _apply_href(row, slug=None, conc=True):
    from compare.models import PDF
    show_row = "match" if conc else "file"
    file, match = row["file"], row[show_row]
    pdf_name = os.path.basename(file).replace(".conllu", "")
    pdf = PDF.objects.get(slug=slug, name=pdf_name)
    path = f"/compare/{slug}?page={pdf.num+1}"
    return f"[{match}]({path})"


def _add_links(df, slug, conc=True):
    """
    add a markdown href to the match

    try/except is basically for runserver/development stuff
    """
    try:
        if not management_handling():
            show_row = "match" if conc else "file"
            df[show_row] = df.apply(_apply_href, axis=1, slug=slug, conc=conc)
    except ObjectDoesNotExist:
        print("Unable to add links, hopefully because this is management command.")
        return df
    return df


def _make_multiword_query(query, col, regex):
    """
    Turns a query with spaces into a multiword depgrep query!

    Vorbericht für jedermann

    becomes

    'w"Vorbericht" + (w"für" + w"jedermann")'
    """
    out = []
    tokens = [i.strip() for i in query.split(" ")]
    boundary = "/" if regex else '"'
    # # A + B       A immediately precedes B.
    rightbracks = ")" * (len(tokens) - 2)
    last_token = len(tokens) - 1
    for i, token in enumerate(tokens):
        leftbrack = "" if i in {0, last_token} else "("
        unit = f"{leftbrack}{col}{boundary}{token}{boundary}"
        if i+1 == len(tokens):
            unit += rightbracks
        out.append(unit)
    return " + ".join(out), len(tokens)


def split_filter_part(filter_part):
    """
    From https://dash.plotly.com/datatable/callbacks
    """
    operators = [['ge ', '>='],
                 ['le ', '<='],
                 ['lt ', '<'],
                 ['gt ', '>'],
                 ['ne ', '!='],
                 ['eq ', '='],
                 ['contains '],
                 ['datestartswith ']]

    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


def _correct_page(corpus, page_current, page_size):
    return corpus.iloc[page_current*page_size:(page_current+1)*page_size]


def _filter_corpus(corpus, filters, doing_search=False):
    if doing_search:
        return corpus, False
    filtering_expressions = filters.split(' && ') if filters is not None else []
    if filtering_expressions:
        for filter_part in filtering_expressions:
            col_name, operator, filter_value = split_filter_part(filter_part)
            if operator in {'eq', 'ne', 'lt', 'le', 'gt', 'ge'}:
                # these operators match pandas series operator method names
                corpus = corpus.loc[getattr(corpus[col_name], operator)(filter_value)]
            elif operator == 'contains':
                corpus = corpus.loc[corpus[col_name].str.contains(filter_value)]
            elif operator == 'datestartswith':
                # this is a simplification of the front-end filtering logic,
                # only works with complete fields in standard format
                corpus = corpus.loc[corpus[col_name].str.startswith(filter_value)]
    return corpus, bool(filtering_expressions)


def _sort_corpus(corpus, sort_by, doing_search=False):
    if doing_search:
        return corpus, False
    # if sorting
    if sort_by and len(sort_by):
        corpus = corpus.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )
    sort_by = bool(len(sort_by)) if sort_by else False
    return corpus, sort_by