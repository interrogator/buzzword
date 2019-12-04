"""
buzzword explorer: callbacks
"""

import pandas as pd
from buzz.dashview import _df_to_figure
from buzz.exceptions import DataTypeError
from dash import no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .helpers import (_cast_query, _get_specs_and_corpus, _special_search,
                      _translate_relative, _tuple_or_list, _update_concordance,
                      _update_conll, _update_frequencies)
from .main import CORPORA, INITIAL_TABLES, app
from .strings import (_make_search_name, _make_table_name, _search_error,
                      _table_error)

# we can't keep tables in dcc.store, they are too big. so we keep all here with
# a tuple that can identify them (ideally, even dealing with user sessions)
FREQUENCY_TABLES = dict()


@app.expanded_callback([Output("input-box", "placeholder"), Output("gram-select", "disabled")], [Input("search-target", "value")])
def _correct_placeholder(value, **kwargs):
    """
    More accurate placeholder text when doing dependencies
    """
    default = "Enter regular expression search query..."
    mapped = {
        "t": "Enter Tgrep2 query...",
        "d": "Enter depgrep query",
        "describe": "Enter depgrep query (e.g. l\"man\")"
    }
    disable_gram = value in mapped
    return mapped.get(value, default), disable_gram


@app.expanded_callback(
    [
        Output("tab-dataset", "style"),
        Output("tab-frequencies", "style"),
        Output("tab-chart", "style"),
        Output("tab-concordance", "style"),
    ],
    [Input("tabs", "value")],
)
def render_content(tab, **kwargs):
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

    @app.expanded_callback(
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
    def _new_chart(n_clicks, table_from, chart_type, top_n, transpose, session_tables, **kwargs):
        """
        Make new chart by kind. Do it 5 times, once for each chart space
        """
        # before anything is loaded, do nothing
        if n_clicks is None:
            return no_update
        # get correct dataset to chart

        this_table = session_tables[str(table_from)]
        df = FREQUENCY_TABLES[_tuple_or_list(this_table, tuple)]

        # transpose and cut down items to plot
        if transpose:
            df = df.T
        df = df.iloc[:, :top_n]
        # generate chart
        return _df_to_figure(df, chart_type)


@app.expanded_callback(
    [Output("loading-main", "className"), Output("loading-main", "fullscreen")],
    [Input("everything", "children")],
    [],
)
def _on_load_callback(n_clicks, **kwargs):
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
        State("gram-select", "value"),
        State("search-from", "options"),
        State("session-configs", "data"),
        State("session-search", "data"),
        State("session-clicks-clear", "data"),
        State("slug", "title"),
    ],
)
def _new_search(
    n_clicks,
    cleared,
    search_from,
    skip,
    col,
    search_string,
    gram_select,
    search_from_options,
    conf,
    session_search,
    session_clicks_clear,
    url,
    **kwargs
):
    """
    Callback when a new search is submitted

    Validate input, run the search, store data and display things
    """
    # the first callback, before anything is loaded
    if n_clicks is None:
        return [no_update] * 10

    slug = url.rstrip("/").split("/")[-1]
    conf = conf[slug]
    add_governor = conf["add_governor"]
    max_row, max_col = conf["table_size"]

    specs, corpus = _get_specs_and_corpus(search_from, session_search, CORPORA, slug)

    msg = _search_error(col, search_string)
    if msg:
        return [no_update, no_update, no_update, no_update, False, True, msg, False, no_update, no_update]

    new_value = len(session_search) + 1

    # on first search, spec is slug name, so it goes here.
    this_search = [specs, col, skip, search_string, gram_select]

    exists = next(
        (i for i in session_search.values() if this_search == list(i)[:5]), False
    )
    if exists:
        msg = "Table already exists. Switching to that one to save memory."
        df = corpus.iloc[exists[-1]]

    # if the user has done clear history
    if cleared and cleared != session_clicks_clear:
        session_search.clear()
        corpus = CORPORA[slug]
        corpus = corpus.iloc[:max_row, :max_col]
        cols, data = _update_conll(corpus, False, drop_govs=add_governor)
        name = _make_search_name(conf["corpus_name"], len(corpus), session_search)
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
        # todo: more cleanup for this, it's ugly!
        # tricky searches
        if col in {"t", "d", "describe"}:
            df, msg = _special_search(corpus, col, search_string, skip)
        # do ngramming stuff
        if gram_select:
            df = getattr(corpus.near, col)(search_string, distance=gram_select)
        # skip/just searches
        elif col not in {"t", "d", "describe"}:
            search = _cast_query(search_string, col)
            method = "just" if not skip else "skip"
            try:
                df = getattr(getattr(corpus, method), col)(search)
            # todo: tell the user the problem?
            except DataTypeError:
                df = df.iloc[:0, :0]
                msg = "Query type problem. Query is {}, col {} is {}."
                if isinstance(search, list):
                    search = search[0]
                msg = msg.format(type(search), col, corpus[col].dtype)
        # if there are no results
        if not len(df) and not msg:
            found_results = False
            msg = "No results found, sorry."

    this_search += [new_value, len(df), list(df["_n"])]
    if found_results:
        session_search[new_value] = _tuple_or_list(this_search, list)
        corpus = CORPORA[slug]
        df = df.iloc[:max_row, :max_col]
        current_cols, current_data = _update_conll(df, True, add_governor)
    else:
        current_cols, current_data = no_update, no_update

    if not msg:
        name = _make_search_name(this_search, len(corpus), session_search)
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


@app.expanded_callback(
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
        State("multiindex-switch", "on"),
        State("chart-from-1", "options"),
        State("chart-from-1", "value"),
        State("session-configs", "data"),
        State("session-search", "data"),
        State("session-tables", "data"),
        State("session-clicks-table", "data"),
        State("slug", "title"),
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
    multiindex_columns,
    table_from_options,
    nv1,
    conf,
    session_search,
    session_tables,
    session_click_table,
    url,
    **kwargs
):
    """
    Callback when a new freq table is generated. Same logic as new_search.
    """
    # do nothing if not yet loaded
    if n_clicks is None:
        return [no_update] * 14

    slug = url.rstrip("/").split("/")[-1]
    conf = conf[slug]

    # because no option below can return initial table, rows can now be deleted
    row_deletable = True

    specs, corpus = _get_specs_and_corpus(search_from, session_search, CORPORA, slug)

    # figure out sort, subcorpora,relative and keyness
    sort = sort or "total"
    if subcorpora == "_corpus":
        subcorpora = None
    relative, keyness = _translate_relative(relkey)

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
    this_table_list = [specs, list(show), subcorpora, relative, keyness, sort]
    this_table_tuple = _tuple_or_list(this_table_list, tuple)

    # if table already made, use that one
    key = next((k for k, v in session_tables.items() if this_table_list == v), False)
    idx = key if key is not False else len(session_tables) + 1

    # if we are updating the table:
    if updating:
        # get the whole table from master dict of them
        table = FREQUENCY_TABLES[this_table_tuple]
        # fix rows and columns
        table = table[[i["id"] for i in current_cols[1:]]]
        table = table.loc[[i["_" + table.index.name] for i in current_data]]
        # store table again with same key
        FREQUENCY_TABLES[this_table_tuple] = table
    elif key is not False:
        msg = "Table already exists. Switching to that one to save memory."
        table = FREQUENCY_TABLES[this_table_tuple]
    # if there was a validation problem, juse use last table (?)
    elif msg:
        if session_tables:
            # todo: figure this out...use current table instead?
            key, value = list(session_tables.items())[-1]
            table = FREQUENCY_TABLES[_tuple_or_list(value, tuple)]
            # todo: more here?
        else:
            table = INITIAL_TABLES[slug]
    else:
        # generate table
        table = corpus.table(
            show=show,
            subcorpora=subcorpora,
            relative=relative if relative != "corpus" else CORPORA[slug],
            keyness=keyness,
            sort=sort,
            multiindex_columns=multiindex_columns
        )
        # round df if floats are used
        if relative is not False or keyness:
            table = table.round(2)

        # cannot hash a corpus, which relative may be. none will denote corpus as reference
        if isinstance(relative, pd.DataFrame):
            relative = None

        # then store the search information in store/freq table spaces
        session_tables[idx] = this_table_list
        FREQUENCY_TABLES[this_table_tuple] = table

    if updating:
        cols, data = no_update, no_update
    else:
        max_row, max_col = conf["table_size"]
        tab = table.iloc[:max_row, :max_col]
        cols, data = _update_frequencies(tab, deletable=True)

    csv_path = "todo"

    if not msg and not updating:
        table_name = _make_table_name(this_table_list)
        option = dict(value=idx, label=table_name)
        table_from_options.append(option)
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


@app.expanded_callback(
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
        State("session-configs", "data"),
        State("session-search", "data"),
        State("slug", "title"),
    ],
)
def _new_conc(n_clicks, show, search_from, conf, session_search, url, **kwargs):
    """
    Callback for concordance. We just pick what to show and where from...
    """
    if n_clicks is None:
        return [no_update] * 4

    slug = url.rstrip("/").split("/")[-1]
    conf = conf[slug]

    # easy validation!
    msg = "" if show else "No choice made for match formatting."
    if not show:
        return no_update, no_update, True, msg

    specs, corpus = _get_specs_and_corpus(search_from, session_search, CORPORA, slug)

    met = ["file", "s", "i"]
    # todo: corpus may not be loaded. then how to know what metadata there is?
    if isinstance(corpus, pd.DataFrame) and "speaker" in corpus.columns:
        met.append("speaker")

    conc = corpus.conc(show=show, metadata=met, window=(100, 100))
    max_row, max_col = conf["table_size"]
    short = conc.iloc[:max_row, :max_col]
    cols, data = _update_concordance(short, deletable=True)
    return cols, data, bool(msg), msg


@app.expanded_callback(Output("matching-text", "children"), [Input("skip-switch", "on")])
def _matching_not_matching(on, **kwargs):
    return "matching" if not on else "not matching"


@app.expanded_callback([Output("multiindex-text", "children"), Output("multiindex-switch", "disabled")], [Input("multiindex-switch", "on"), Input("show-for-table", "value")])
def _multiindex(on, show, **kwargs):
    if not show or len(show) < 2:
        return "", True
    text = "Join columns" if not on else "Multiple column levels"
    return text, False
