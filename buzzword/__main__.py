"""
buzzword: main file.

Get the needed data from .parts.main, and provide the callback for URL bar.

By calling it __main__.py, we can start the app with `python -m buzzword`
"""

import os

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .parts import start, explore  # noqa: F401
from .parts.main import app, server  # noqa: F401
from .parts.main import ROOT, CORPORA, CORPUS_META, CORPORA_CONFIGS
from .parts.tabs import _make_tabs
from .parts.helpers import _get_corpus, _get_initial_table

# where downloadable CSVs/corpora get stored
for path in {"csv", "uploads"}:
    if not os.path.isdir(path):
        os.makedirs("csv")


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
    configs = dcc.Store(id="uploaded-configs", data=dict())
    content = html.Div(id="page-content")
    stores = [search_store, tables_store, click_clear, click_table, configs]
    return html.Div([loc] + stores + [content])


app.layout = _get_layout

LAYOUTS = dict()


def _make_explore_layout(slug, conf):
    """
    Simulate globals and generate layout for explore page
    """
    from buzzword.parts.start import CORPORA, INITIAL_TABLES, CORPORA_CONFIGS

    corpus = _get_corpus(slug)
    table = _get_initial_table(slug)
    size = conf.get("len", len(corpus))
    conf["slug"] = slug  # can i delete this?
    return _make_tabs(corpus, table, conf)


def _populate_explore_layouts():
    """
    Can be used to create explore page on startup, save loading time

    broken right now, unused
    """
    for name, meta in CORPUS_META.items():
        slug = meta["slug"]
        LAYOUTS[slug] = _make_explore_layout(slug, meta)


def _get_explore_layout(slug, uploaded_configs):
    """
    Get (and maybe generate) the explore layout for this slug
    """
    from buzzword.parts.start import CORPORA_CONFIGS
    upped = uploaded_configs.get(slug)
    conf = CORPORA_CONFIGS.get(slug, upped)
    if not conf:
        return
    # store the default explore for each corpus in a dict for speed
    if slug in LAYOUTS:
        return LAYOUTS[slug]
    layout = _make_explore_layout(slug, conf)
    LAYOUTS[slug] = layout
    return layout


@app.callback(Output("page-content", "children"), [Input("url", "pathname")], [State("uploaded-configs", "data")])
def _choose_correct_page(pathname, configs):
    """
    When the URL changes, get correct page and populate page-content with it
    """
    if pathname is None:
        raise PreventUpdate
    pathname = pathname.lstrip("/")
    if pathname.startswith("explore"):
        slug = pathname.rstrip("/").split("/")[-1]
        # if corpus not found, redirect
        if slug not in CORPORA:
            pathname = ""
        layout = _get_explore_layout(slug, configs)
        if layout:
            return layout
        print("LAYOUT ERROR: ", slug, list(CORPORA.keys()))
    if not pathname:
        return start.layout
    else:
        return "404. Page not found: {}".format(pathname)


if __name__ == "__main__":
    app.run_server(debug=True)
