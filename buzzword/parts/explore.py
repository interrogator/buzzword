"""
buzzword: callbacks for explore page
"""

import os
import pandas as pd

from buzz.dashview import _df_to_figure
from buzzword.parts.helpers import (
    _get_specs_and_corpus,
    _translate_relative,
    _update_datatable,
    _get_table_for_chart,
)
from buzzword.parts.strings import (
    _make_search_name,
    _make_table_name,
    _search_error,
    _table_error,
)
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import flask

from buzzword.parts.main import app, CONFIG, CORPORA, INITIAL_TABLES

# we can't keep tables in dcc.store, they are too big. so we keep all here with
# a tuple that can identify them (ideally, even dealing with user sessions)
FREQUENCY_TABLES = dict()

#############
# CALLBACKS #
#############
#
@app.callback(Output("input-box", "placeholder"), [Input("search-target", "value")])
def _correct_placeholder(value):
    """
    More accurate placeholder text when doing dependencies
    """
    if value == "d":
        return "Enter depgrep query..."
    else:
        return "Enter regular expression search query..."


@app.callback(
    [
        Output("tab-dataset", "style"),
        Output("tab-frequencies", "style"),
        Output("tab-chart", "style"),
        Output("tab-concordance", "style"),
    ],
    [Input("tabs", "value")],
)
def render_content(tab):
    """
    Tab display callback. If the user clicked this tab, show it, otherwise hide
    """
    if tab is None:
        tab = "dataset"
    outputs = []
    for i in ["dataset", "frequencies", "chart", "concordance"]:
        if tab == i:
            outputs.append({"display": "block"})
        else:
            outputs.append({"display": "none"})
    return outputs


# one for each chart space
for i in range(1, 6):

    @app.callback(
        Output(f"chart-{i}", "figure"),
        [Input(f"figure-button-{i}", "n_clicks")],
        [
            State(f"chart-from-{i}", "value"),
            State(f"chart-type-{i}", "value"),
            State(f"chart-top-n-{i}", "value"),
            State(f"chart-transpose-{i}", "on"),
            State("session-tables", "data"),
        ],
    )
    def _new_chart(n_clicks, table_from, chart_type, top_n, transpose, session_tables):
        """
        Make new chart by kind. Do it 5 times, once for each chart space
        """
        # before anything is loaded, do nothing
        if n_clicks is None:
            raise PreventUpdate
        # get correct dataset to chart
        df = _get_table_for_chart(table_from, session_tables, FREQUENCY_TABLES)
        # transpose and cut down items to plot
        if transpose:
            df = df.T
        df = df.iloc[:, :top_n]
        # generate chart
        return _df_to_figure(df, chart_type)


@app.callback(
    [Output("loading-main", "className"), Output("loading-main", "fullscreen")],
    [Input("everything", "children")],
    [],
)
def _on_load_callback(n_clicks):
    """
    This gets triggered on load; we use it to fix loading screen
    """
    return "loading-non-main", False


@app.callback(
    [
        Output("conll-view", "columns"),
        Output("conll-view", "data"),
        Output("search-from", "options"),
        Output("search-from", "value"),
        Output("search-from", "disabled"),
        Output("dialog-search", "displayed"),
        Output("dialog-search", "message"),
        Output("conll-view", "row_deletable"),
        Output("session-search", "data"),
        Output("session-clicks-clear", "data"),
    ],
    [Input("search-button", "n_clicks"), Input("clear-history", "n_clicks")],
    [
        State("search-from", "value"),
        State("skip-switch", "on"),
        State("search-target", "value"),
        State("input-box", "value"),
        State("search-from", "options"),
        State("conll-view", "columns"),
        State("conll-view", "data"),
        State("corpus-slug", "children"),
        State("session-search", "data"),
        State("session-clicks-clear", "data"),
    ],
)
def _new_search(
    n_clicks,
    cleared,
    search_from,
    skip,
    col,
    search_string,
    search_from_options,
    current_cols,
    current_data,
    slug,
    session_search,
    session_clicks_clear,
):
    """
    Callback when a new search is submitted

    Validate input, run the search, store data and display things
    """
    # the first callback, before anything is loaded
    if n_clicks is None:
        raise PreventUpdate
        # can i delete the below?
        return (
            current_cols,
            current_data,
            search_from_options,
            search_from,
            True,
            False,
            "",
            False,
            session_search,
            session_clicks_clear,
        )

    add_governor = CONFIG["add_governor"]
    max_row, max_col = CONFIG["table_size"]

    specs, corpus = _get_specs_and_corpus(search_from, session_search, CORPORA, slug)

    msg = _search_error(col, search_string)
    if msg:
        return (
            current_cols,
            current_data,
            search_from_options,
            search_from,
            False,
            True,
            msg,
            False,
            session_search,
            session_clicks_clear,
        )

    new_value = len(session_search) + 1

    # on first search, spec is slug name, so it goes here.
    this_search = [specs, col, skip, search_string]

    exists = next(
        (i for i in session_search.values() if this_search == list(i)[:4]), False
    )
    if exists:
        msg = "Table already exists. Switching to that one to save memory."
        df = corpus.iloc[exists[-1]]

    # if the user has done clear history
    if cleared and cleared != session_clicks_clear:
        session_search.clear()
        corpus = CORPORA[slug]
        corpus = corpus.iloc[:max_row, :max_col]
        cols, data = _update_datatable(corpus, corpus, drop_govs=add_governor)
        name = _make_search_name(CONFIG["corpus_name"], len(corpus))
        search_from = [dict(value=0, label=name)]
        # set number of clicks at last moment
        session_clicks_clear = cleared
        return (
            cols,
            data,
            search_from,
            0,
            True,
            False,
            "",
            False,
            session_search,
            session_clicks_clear,
        )

    found_results = True

    if not exists:
        # the expected callback. run a search and update dataset view and search history
        if col == "t":
            df = corpus.tgrep(search_string, inverse=skip)
        elif col == "d":
            try:
                df = corpus.depgrep(search_string, inverse=skip)
            except Exception as error:
                # todo: handle invalid queries properly...
                # we need to give hepful message back to user...
                print(f"DEPGREP ERROR: {type(error)}: {error}")
                # after which, either we return previous, or return none:
                df = df.iloc[:0, :0]
        else:
            method = "just" if not skip else "skip"
            df = getattr(getattr(corpus, method), col)(search_string.strip())
        # if there are no results
        if not len(df):
            found_results = False
            msg = "No results found, sorry."

    this_search += [new_value, len(df), list(df["_n"])]
    if found_results:
        session_search[new_value] = this_search
        corpus = CORPORA[slug]
        df = df.iloc[:max_row, :max_col]
        current_cols, current_data = _update_datatable(
            corpus, df, drop_govs=add_governor, deletable=True
        )
    if not msg:
        name = _make_search_name(this_search, len(corpus))
        option = dict(value=new_value, label=name)
        search_from_options.append(option)
    elif exists:
        new_value = exists[-3]
    else:
        new_value = search_from
    return (
        current_cols,
        current_data,
        search_from_options,
        new_value,
        False,
        bool(msg),
        msg,
        True,
        session_search,
        session_clicks_clear,
    )


@app.callback(
    [
        Output("freq-table", "columns"),
        Output("freq-table", "data"),
        Output("chart-from-1", "value"),
        Output("chart-from-1", "options"),
        Output("chart-from-2", "options"),
        Output("chart-from-3", "options"),
        Output("chart-from-4", "options"),
        Output("chart-from-5", "options"),
        Output("dialog-table", "displayed"),
        Output("dialog-table", "message"),
        Output("freq-table", "row_deletable"),
        Output("download-link", "href"),
        Output("session-tables", "data"),
        Output("session-clicks-table", "data"),
    ],
    [
        Input("table-button", "n_clicks"),
        Input("freq-table", "columns_previous"),
        Input("freq-table", "data_previous"),
    ],
    [
        State("freq-table", "columns"),
        State("freq-table", "data"),
        State("search-from", "value"),
        State("show-for-table", "value"),
        State("subcorpora-for-table", "value"),
        State("relative-for-table", "value"),
        State("sort-for-table", "value"),
        State("chart-from-1", "options"),
        State("chart-from-1", "value"),
        State("corpus-slug", "children"),
        State("session-search", "data"),
        State("session-tables", "data"),
        State("session-clicks-table", "data"),
    ],
)
def _new_table(
    n_clicks,
    prev_cols,
    prev_data,
    current_cols,
    current_data,
    search_from,
    show,
    subcorpora,
    relkey,
    sort,
    table_from_options,
    nv1,
    slug,
    session_search,
    session_tables,
    session_click_table,
):
    """
    Callback when a new freq table is generated. Same logic as new_search.
    """
    # do nothing if not yet loaded
    if n_clicks is None:
        raise PreventUpdate

    # because no option below can return initial table, rows can now be deleted
    row_deletable = True

    specs, corpus = _get_specs_and_corpus(search_from, session_search, CORPORA, slug)

    if not sort:
        sort = "total"

    relative, keyness = _translate_relative(relkey, CORPORA[slug])

    # check if there are any validation problems
    if session_click_table != n_clicks:
        updating = False
        session_click_table = n_clicks
    elif prev_data is not None:
        # if number of rows has changed
        if len(prev_data) != len(current_data):
            updating = True
        # if number of columns has changed
        if len(prev_data[0]) != len(current_data[0]):
            updating = True

    msg = _table_error(show, subcorpora, updating)
    idx = len(session_tables) + 1
    this_table = [specs, show, subcorpora, relative, keyness, sort, idx, 0]

    # if table already made, use that one
    key, exists = next(
        ((k, v) for k, v in session_tables.items() if this_table[:6] == v[:6]),
        (False, False),
    )

    # if we are updating the table:
    if updating:
        table = FREQUENCY_TABLES[tuple(exists[:6])]
        exists[-1] += 1
        # fix rows and columns
        table = table[[i["id"] for i in current_cols[1:]]]
        table = table.loc[[i["_" + table.index.name] for i in current_data]]
        # store again
        session_tables[key] = exists
        FREQUENCY_TABLES[tuple(exists[:6])] = table
    elif exists:
        msg = "Table already exists. Switching to that one to save memory."
        table = FREQUENCY_TABLES[tuple(exists[:6])]
    # if there was a validation problem, juse use last table (?)
    elif msg:
        if session_tables:
            # todo: figure this out...use current table instead?
            key, value = list(session_tables.items())[-1]
            table = FREQUENCY_TABLES[tuple(value[:6])]
            # todo: more here?
        else:
            table = INITIAL_TABLES[slug]
    else:
        # generate table
        table = corpus.table(
            show=show,
            subcorpora=subcorpora,
            relative=relative,
            keyness=keyness,
            sort=sort,
        )
        # round df if floats are used
        if relative is not False or keyness:
            table = table.round(2)

        # cannot hash a corpus, which relative may be. none will denote corpus as reference
        if isinstance(relative, pd.DataFrame):
            relative = None

        # make show a tuple, then store the search information
        this_table[1] = tuple(this_table[1])
        session_tables[idx] = this_table

    if updating:
        cols, data = current_cols, current_data
    else:
        max_row, max_col = CONFIG["table_size"]
        tab = table.iloc[:max_row, :max_col]
        cols, data = _update_datatable(CORPORA[slug], tab, conll=False)

    csv_path = "todo"

    if not msg and not updating:
        table_name = _make_table_name(this_table)
        option = dict(value=idx, label=table_name)
        table_from_options.append(option)
    elif exists or updating:
        idx = key
    return (
        cols,
        data,
        idx,
        table_from_options,
        table_from_options,
        table_from_options,
        table_from_options,
        table_from_options,
        bool(msg),
        msg,
        row_deletable,
        csv_path,
        session_tables,
        session_click_table,
    )


@app.callback(
    [
        Output("conc-table", "columns"),
        Output("conc-table", "data"),
        Output("dialog-conc", "displayed"),
        Output("dialog-conc", "message"),
    ],
    [Input("update-conc", "n_clicks")],
    [
        State("show-for-conc", "value"),
        State("search-from", "value"),
        State("conc-table", "columns"),
        State("conc-table", "data"),
        State("corpus-slug", "children"),
        State("session-search", "data"),
    ],
)
def _new_conc(n_clicks, show, search_from, cols, data, slug, session_search):
    """
    Callback for concordance. We just pick what to show and where from...
    """
    if n_clicks is None:
        raise PreventUpdate

    # easy validation!
    msg = "" if show else "No choice made for match formatting."
    if not show:
        return cols, data, True, msg

    specs, corpus = _get_specs_and_corpus(search_from, session_search, CORPORA, slug)

    met = ["file", "s", "i"]

    # corpus may not be loaded. then how to know what metadata there is?
    if isinstance(corpus, pd.DataFrame) and "speaker" in corpus.columns:
        met.append("speaker")

    conc = corpus.conc(show=show, metadata=met, window=(100, 100))
    max_row, max_col = CONFIG["table_size"]
    short = conc.iloc[:max_row, :max_col]
    cols, data = _update_datatable(CORPORA[slug], short, conc=True)
    return cols, data, bool(msg), msg


@app.server.route("/csv/<path:path>")
def serve_static(path):
    """
    Download the file at the specified path
    """
    root_dir = os.path.join(os.getcwd(), "csv")
    return flask.send_from_directory(root_dir, path)
