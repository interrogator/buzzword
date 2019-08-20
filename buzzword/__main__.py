import os
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from .parts import start, explore  # noqa: F401
from .parts.main import server  # noqa: F401
from .parts.main import CONFIG, CORPORA, CORPUS_META, INITIAL_TABLES, app
from .parts.tabs import _make_tabs

# where downloadable CSVs get stored
if not os.path.isdir("csv"):
    os.makedirs("csv")
# where uploaded corpora are stored
if not os.path.isdir("uploads"):
    os.makedirs("uploads")


def _get_layout():
    """
    Function for layout. Could be helpful in future to do it this way.
    """
    loc = dcc.Location(id="url", refresh=False)
    search_store = dcc.Store(id='session-search', data=dict())
    tables_store = dcc.Store(id='session-tables', data=dict())
    click_clear = dcc.Store(id='session-clicks-clear')
    click_table = dcc.Store(id='session-clicks-table')
    content = html.Div(id="page-content")
    stores = [search_store, tables_store, click_clear, click_table]
    return html.Div([loc] + stores + [content])


app.layout = _get_layout

LAYOUTS = dict()


def _make_explore_layout(slug, name):
    """
    Simulate globals and generate layout for explore page
    """
    corpus = CORPORA[slug]
    size = CORPUS_META[name].get("len", len(corpus))
    args = [CORPORA[slug], INITIAL_TABLES[slug], slug, name]
    return _make_tabs(*args, corpus_size=size, **CONFIG)


def _populate_explore_layouts():
    """
    Can be used to create explore page on startup, save loading time
    """
    for name, meta in CORPUS_META.items():
        slug = meta["slug"]
        LAYOUTS[slug] = _make_explore_layout(slug, name)


def _get_explore_layout(slug):
    """
    Get (and maybe generate) the explore layout for this slug
    """
    gen = (k for k, v in CORPUS_META.items() if v["slug"] == slug)
    name = next(gen, None)
    name = name or slug
    # store the default explore for each corpus in a dict for speed
    if slug in LAYOUTS:
        return LAYOUTS[slug]
    layout = _make_explore_layout(slug, name)
    LAYOUTS[slug] = layout
    return layout


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def _choose_correct_page(pathname):
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
        return _get_explore_layout(slug)
    if not pathname:
        return start.layout
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=True)
