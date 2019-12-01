"""
buzzword explorer: helpers and utilities
"""

import json
import os

import pandas as pd
from buzz.constants import SHORT_TO_COL_NAME, SHORT_TO_LONG_NAME
from buzz.corpus import Corpus

from .strings import _capitalize_first, _downloadable_name
from explore.models import Corpus as CorpusModel

def _get_specs_and_corpus(search_from, searches, corpora, slug):
    """
    Get the correct corpus based on search_from
    """
    from .main import ROOT

    # if corpus not loaded into corpora, it is an upload. fix now
    if not corpora:
        upload = os.path.join(ROOT, "uploads", slug + "-parsed")
        loaded = Corpus(upload).load()
        corpora[slug] = loaded
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


def _update_datatable(
    corpus, df, conll=True, conc=False, drop_govs=False, deletable=True
):
    """
    Make columns and data for datatable display
    """
    conll = conll if not conc else False
    if conll:
        df = _drop_cols_for_datatable(df, drop_govs)
        col_order = ["file", "s", "i"] + list(df.columns)
    elif conc:
        col_order = ["left", "match", "right", "file", "s", "i"]
        if "speaker" in df.columns:
            col_order.append("speaker")
    # for frequency table: rename index in case 'file' appears in columns
    else:
        names = ["_" + str(x) for x in df.index.names]
        df.index.names = names
        col_order = list(df.index.names) + list(df.columns)
    # concordance doesn't need resetting, because index is unhelpful
    if not conc:
        df = df.reset_index()
    df = df[[i for i in col_order if i is not None]]
    cannot_delete = {"s", "i"} if conll else {"left", "match", "right"}
    if conll or conc:
        columns = [
            {
                "name": _capitalize_first(SHORT_TO_COL_NAME.get(i, i)),
                "id": i,
                "deletable": i not in cannot_delete and deletable,
            }
            for i in df.columns
        ]
    else:
        columns = [
            {
                "name": i.lstrip("_"),
                "id": i,
                "deletable": deletable and "_" + i not in names,
            }
            for i in df.columns
        ]
    return columns, df.to_dict("rows")


def _preprocess_corpus(corpus, max_dataset_rows, drop_columns, **kwargs):
    """
    Fix corpus if the user wants this on command line
    """
    if max_dataset_rows is not None:
        corpus = corpus.iloc[:max_dataset_rows, :]
    if drop_columns is not None:
        corpus = corpus.drop(drop_columns, axis=1, errors="ignore")
    return corpus


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
    from .main import ROOT, CORPORA

    if slug in CORPORA:
        return CORPORA[slug]
    upload = os.path.join(ROOT, "uploads", slug + "-parsed")
    corpus = Corpus(upload).load()
    CORPORA[slug] = corpus
    return corpus


def _get_initial_table(slug):
    """
    Get or create the initial table for this slug
    """
    # todo: speed up by storing as INITIAL_TABLES?
    corpus = _get_corpus(slug)
    return corpus.table(show="p", subcorpora="file")


def _cast_query(query, col):
    """
    ALlow different query types (e.g. numerical, list, str)
    """
    query = query.strip()
    if col in {'t', 'd'}:
        return query
    if query.startswith("[") and query.endswith(']'):
        if ',' in query:
            query = ','.split(query[1:-1])
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
    from . import callbacks

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

def _get_corpora_meta(corpora_file):
    contents = _get_corpora_json_contents(corpora_file)
    corpora = []
    for corpus_name, corpus_json in contents.items():
        corpora.append(CorpusModel.from_json(corpus_json, corpus_name))
    return corpora

def _special_search(df, col, search_string, skip):
    """
    Perform nonstandard search types (tgrep, depgrep, describe)

    todo: proper error handling etc
    """
    mapped = dict(t="tgrep", d="depgrep", describe="describe")
    try:
        # note, describe inverse is nonfunctional!
        matches = getattr(df, mapped[col])(search_string, inverse=skip)
        return matches, None
    except Exception as error:
        msg = f"search error for {col} ({search_string}): {type(error)}: {error}"
        print(msg)
        return df.iloc[:0, :0], msg
