"""
buzzword: main file.

Get the needed data from .parts.main, and provide the callback for URL bar.

By calling it __main__.py, we can start the app with `python -m buzzword`
"""

import os

import dash_core_components as dcc
import dash_html_components as html
import dpd_components as dpd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .parts import explore  # noqa: F401
from .parts.helpers import _get_corpus, _get_initial_table
from .parts.main import (CORPORA, CORPORA_CONFIGS, CORPUS_META,  # noqa: F401
                         app)
from .parts.tabs import _make_tabs

# where downloadable CSVs/corpora get stored
for path in {"csv", "uploads"}:
    if not os.path.isdir(path):
        os.makedirs(path)


def _get_layout():
    """
    Function for layout. Could be helpful in future to do it this way.
    """
    loc = dcc.Location(id="url", refresh=False)
    # user storage for searches, tables, and click counts
    search_store = dcc.Store(id="session-search", data=dict())
    tables_store = dcc.Store(id="session-tables", data=dict())
    click_clear = dcc.Store(id="session-clicks-clear", data=-1)
    click_table = dcc.Store(id="session-clicks-table", data=-1)
    configs = dcc.Store(id="session-configs", data=CORPORA_CONFIGS)
    content = html.Div(id="page-content")
    stores = [search_store, tables_store, click_clear, click_table, configs]
    return html.Div([loc] + stores + [content])


app.layout = _get_layout

LAYOUTS = dict()


def _make_explore_layout(slug, conf, configs):
    """
    Simulate globals and generate layout for explore page
    """
    corpus = _get_corpus(slug)
    table = _get_initial_table(slug)
    conf["len"] = conf.get("len", len(corpus))
    conf["slug"] = slug  # can i delete this?
    return _make_tabs(corpus, table, conf, configs)


def _populate_explore_layouts():
    """
    Can be used to create explore page on startup, save loading time

    broken right now, unused
    """
    for name, meta in CORPUS_META.items():
        slug = meta["slug"]
        LAYOUTS[slug] = _make_explore_layout(slug, meta)


def _get_explore_layout(slug, all_configs):
    """
    Get (and maybe generate) the explore layout for this slug
    """
    conf = all_configs.get(slug)
    if not conf:
        return
    # store the default explore for each corpus in a dict for speed
    if slug in LAYOUTS:
        return LAYOUTS[slug]
    layout = _make_explore_layout(slug, conf, all_configs)
    LAYOUTS[slug] = layout
    return layout
