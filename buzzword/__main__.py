import os
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from .parts import explore  # noqa: F401
from .parts import about, building, depgrep, guide, start
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
    content = html.Div(id="page-content")
    return html.Div([loc, content])


app.layout = _get_layout

LAYOUTS = dict()


def _make_explore_layout(slug, name):
    """
    Simulate globals and generate layout for explore page
    """
    corpus = CORPORA[slug]
    searches = OrderedDict({name: corpus})
    tables = OrderedDict({"initial": INITIAL_TABLES[slug]})
    return _make_tabs(searches, tables, slug, **CONFIG)


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
    pages = dict(
        about=about.layout,
        guide=guide.layout,
        building=building.layout,
        start=start.layout,
        depgrep=depgrep.layout,
    )
    pathname = pathname
    if pathname is None:
        raise PreventUpdate
    if not pathname:
        return start.layout
    if pathname in pages:
        return pages[pathname]
    if pathname.startswith("explore"):
        slug = pathname.rstrip("/").split("/")[-1]
        # if corpus not found, redirect
        if slug not in CORPORA:
            return start.layout
        # find corpus name by slug
        return _get_explore_layout(slug)
    if pathname in {"", "/"}:
        return start.layout
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=True)
