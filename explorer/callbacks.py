"""
buzzword explorer: callbacks
"""
from datetime import datetime
import json
from math import ceil
import os
import pandas as pd
from buzz.exceptions import DataTypeError
from dash import no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from explore.models import Corpus as CorpusModel
from explore.models import SearchResult, TableResult

from django.contrib.auth.models import User
from django.conf import settings
from .chart import _df_to_figure

from . import helpers

from .lang import LANGUAGES

from .main import app
from .strings import _make_search_name, _make_table_name, _search_error, _table_error

from . import style


from buzzword.utils import management_handling, delete_old_tables

if not management_handling():
    from start.apps import corpora, initial_tables, initial_concs, user_tables


@app.expanded_callback(
    Output("input-box", "placeholder"),  # Output("gram-select", "disabled")],  # swisslaw
    [Input("search-target", "value")],
    [State("language-switch", "on")],
)
def _correct_placeholder(value, lang, **kwargs):
    """
    More accurate placeholder text when doing dependencies
    """
    if value is None:
        return no_update

    return "Enter search query..." if not lang else "Suchabfrage eingeben..."

    # tofix
    mapped = {
        "t": "Enter Tgrep2 query...",
        "d": "Enter depgrep query",
        "describe": 'Enter depgrep query (e.g. l"man" = f"nsubj")',
    }
    # disable_gram = value in mapped
    return mapped.get(value, default)  # , disable_gram


@app.expanded_callback(
    [
        Output("tab-dataset", "style"),
        Output("tab-frequencies", "style"),
        Output("tab-chart", "style"),
        Output("tab-concordance", "style"),
    ],
    [Input("tabs", "value")],
    [State("search-from", "value")],
)
def render_content(tab, search_from, **kwargs):
    """
    Tab display callback. If the user clicked this tab, show it, otherwise hide
    """
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
            State("slug", "title"),
        ],
    )
    def _new_chart(
        n_clicks, table_from, chart_type, top_n, transpose, session_tables, slug, **kwargs,
    ):
        """
        Make new chart by kind. Do it 5 times, once for each chart space
        """
        # before anything is loaded, do nothing
        if n_clicks is None:
            return no_update
        # get correct dataset to chart
        conf = CorpusModel.objects.get(slug=slug)

        if str(table_from) in session_tables:
            this_table = session_tables[str(table_from)]
            df = user_tables[helpers._tuple_or_list(this_table, tuple)]
        else:
            df = initial_tables[slug]

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
    delete_old_tables()
    return "loading-non-main", False


def _filter_view(corpus, page_current, page_size, editable, add_governor, slug):
    """
    Helper to return when just filtering corpus
    """
    filtered_corpus_size = len(corpus)
    corpus = helpers._correct_page(corpus, page_current, page_size)
    cols, data = helpers._update_conll(corpus, editable, drop_govs=add_governor, slug=slug)
    return (
        cols,
        data,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        ceil(filtered_corpus_size / page_size),
    )


def _sort_view(corpus, page_current, page_size, editable, add_governor, slug):
    """
    Helper to return when just sorting corpus
    """
    corpus = helpers._correct_page(corpus, page_current, page_size)
    cols, data = helpers._update_conll(corpus, editable, drop_govs=add_governor, slug=slug)
    return (
        cols,
        data,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
    )


def _pagechange_view(corpus, page_current, page_size, editable, add_governor, slug):
    """
    Helper to return when just changing pages
    """
    corpus_size = len(corpus)
    corpus = helpers._correct_page(corpus, page_current, page_size)
    cols, data = helpers._update_conll(corpus, editable, drop_govs=add_governor, slug=slug)
    return (
        cols,
        data,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        page_current,
        ceil(corpus_size / page_size),
    )



def _show_dataset_view(corpus, page_current, page_size, editable, add_governor, slug, show_dataset=None):
    """
    Helper to return when just showing a different dataset
    """
    corpus_size = len(corpus)
    corpus = helpers._correct_page(corpus, page_current, page_size)
    cols, data = helpers._update_conll(corpus, editable, drop_govs=add_governor, slug=slug)
    return (
        cols,
        data,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        show_dataset,
        no_update,
        no_update,
        ceil(corpus_size / page_size),
    )



def _actual_search(corpus, col, search_string, skip, multiword, no_use_regex):
    """
    # do ngramming stuff...disabled for now
    # if gram_select:
    #   df = getattr(corpus.near, col)(search_string, distance=gram_select)
    # skip/just searches

    Returns: df/None, msg/None
    """
    # depgrep/tgrep search types
    if col in {"t", "d", "describe"}:
        df, msg = helpers._special_search(corpus, col, search_string, skip, multiword)
        if msg:
            return None, msg
        return df, None
    search = helpers._cast_query(search_string, col)
    method = "just" if not skip else "skip"
    extra = dict() if no_use_regex else dict(regex=False, exact_match=True)
    # try to do the just/skip search
    try:
        df = getattr(getattr(corpus, method), col)(search, **extra)
        # check for matches
        if df is not None and len(df):
            return df, None
        return None, "No results found, sorry."
    except Exception as err:
        msg = f"Search error: {str(err)}"
        return None, msg


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
        Output("session-clicks-clear", "data"),
        Output("session-clicks-show", "data"),
        Output("session-clicks-search", "data"),
        Output("session-current-conll-page", "data"),
        Output("conll-view", "page_count"),
    ],
    [
        Input("search-button", "n_clicks"),
        Input("clear-history", "n_clicks"),
        Input("show-this-dataset", "n_clicks"),
        Input("conll-view", "page_current"),
        Input("conll-view", "sort_by"),
        Input("conll-view", "filter_query"),
    ],
    [
        State("search-from", "value"),
        State("skip-switch", "on"),
        State("search-target", "value"),
        State("input-box", "value"),
        State("use-regex", "on"),
        # State("gram-select", "value"),
        State("search-from", "options"),
        State("session-clicks-clear", "data"),
        State("session-clicks-show", "data"),
        State("session-clicks-search", "data"),
        State("session-user-id", "data"),
        State("slug", "title"),
        State("language-switch", "on"),
        State("session-current-conll-page", "data"),
    ],
)
def _new_search(
    n_clicks,
    cleared,
    show_dataset,
    page_current,
    sort_by,
    filters,
    search_from,
    skip,
    col,
    search_string,
    no_use_regex,
    # gram_select,
    search_from_options,
    session_clicks_clear,
    session_clicks_show,
    session_clicks_search,
    user_id,
    slug,
    lang,
    conll_page,
    **kwargs,
):
    """
    Callback when a new search is submitted

    Validate input, run the search, store data and display things
    """
    delete_old_tables()
    # the first callback, before anything is loaded. Just do nothing
    user = User.objects.get(id=user_id)
    conf = CorpusModel.objects.get(slug=slug)
    corpus = helpers._get_corpus(slug)

    clearing_history = cleared is not None and cleared > session_clicks_clear
    showing_dataset = show_dataset and show_dataset != session_clicks_show
    doing_search = n_clicks is not None and n_clicks > session_clicks_search

    if n_clicks is None \
            and show_dataset is None \
            and page_current == conll_page \
            and not sort_by \
            and not clearing_history \
            and not filters:
        search_from_options = helpers._make_search_from(user, slug, conf.name, len(corpus))
        # print(search_from_options)

        return [
            no_update,
            no_update,
            search_from_options,
            search_from,
            True if len(search_from_options) == 1 else False,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update
        ]

    searching_from = None
    uniq = dict(slug=slug, user=user, idx=search_from)
    if search_from:
        searching_from = SearchResult.objects.get(**uniq)

    already = dict(
        slug=slug,
        user=user,
        regex=not no_use_regex,
        target=col,
        query=search_string,
        parent=searching_from
    )
    try:
        exists = SearchResult.objects.get(**already)
    except SearchResult.DoesNotExist:
        exists = None

    # some constants
    max_row, max_col = settings.TABLE_SIZE
    corpus_size = len(corpora[slug])
    editable = bool(search_from)
    # get the corpus and cut it down based on the parent
    if searching_from:
        corpus = corpus.iloc[json.loads(searching_from.indices)]

    # if the user has done clear history, restore the tool to default state
    # we have to do this near the top, because otherwise sorting can get caught
    if clearing_history:
        # remove previous searches
        to_delete = dict(user=user, slug=slug)
        d = SearchResult.objects.filter(**to_delete).delete()
        # get the whole corpus and paginate it
        corpus = corpora[slug]
        corpus_size = len(corpus)
        corpus = helpers._correct_page(corpus, page_current, settings.PAGE_SIZE)
        cols, data = helpers._update_conll(corpus, False, drop_govs=conf.add_governor, slug=slug)
        name = _make_search_name(conf.name, corpus_size, int(lang))
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
            session_clicks_clear,
            session_clicks_show,
            0,
            conll_page,
            ceil(corpus_size / settings.PAGE_SIZE),
        )


    # collect the values we need for returning from sorting, pagination, filtering etc.
    sort_page_filter = [page_current, settings.PAGE_SIZE, editable, conf.add_governor, slug]

    # do filtering. if anything was done, filtered is true, and return via helper
    corpus, filtered = helpers._filter_corpus(corpus, filters, doing_search)
    if filtered and not doing_search:
        return _filter_view(corpus, *sort_page_filter)

    # do sorting. if anything was done, corpus_sorted is true
    corpus, corpus_sorted = helpers._sort_corpus(corpus, sort_by, doing_search)
    # if just sorting, or if sort was returned to normal (2nd case), return
    # todo, may need to improve this...
    if (corpus_sorted and not doing_search and not showing_dataset) or (not sort_by and not doing_search and not showing_dataset):
        print("SORT VIEW")
        return _sort_view(corpus, *sort_page_filter)

    # if changing page, return the correct page data
    if conll_page != page_current:
        print("PAGE CHANGE VIEW")
        return _pagechange_view(corpus, *sort_page_filter)

    # user clicked the show button, show the selected (i.e. search_from) corpus
    if showing_dataset:
        print("SHOWING", search_from, show_dataset, search_from_options, corpus.head(5))
        return _show_dataset_view(corpus, *sort_page_filter, show_dataset=show_dataset)

    # there's a problem with the search
    # todo: use messaging framework for this, not alert popup
    msg = _search_error(col, search_string)
    if msg:
        print("SEARCH ERROR VIEW")
        return [
            no_update,
            no_update,
            no_update,
            no_update,
            True if len(search_from_options) == 1 else False,
            True,
            msg,
            False,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        ]
    # have we already done this exact search? compare previous searches for same data
    # if we have done it, we can return that one instead.
    if exists:
        msg = "Table already exists. Switching to that one to save memory."
        df = corpus.iloc[json.loads(exists.indices)]
        num_pages = ceil(len(df) / settings.PAGE_SIZE)
        df, _ = helpers._filter_corpus(df, filters, False)
        df, _ = helpers._sort_corpus(df, sort_by, False)
        df = helpers._correct_page(df, page_current, settings.PAGE_SIZE)
        cols, data = helpers._update_conll(df, bool(search_from), drop_govs=conf.add_governor, slug=slug)
        # print("EXISTS", search_from_options, exists.idx, exists.parent, exists.order)
        return (
            cols,
            data,
            no_update,
            exists.idx,
            False,
            True,
            msg,
            True,
            no_update,
            no_update,
            n_clicks,
            conll_page,
            ceil(corpus_size / settings.PAGE_SIZE),
        )

    # if the query has spaces, we need to prepare for multiword search
    multiword = " " in search_string.strip()
    if multiword:
        search_string, multiword = helpers._make_multiword_query(search_string.strip(), col, no_use_regex)
        col = "d"

    # DO THE ACTUAL SEARCH HERE
    df, msg = _actual_search(corpus, col, search_string, skip, multiword, no_use_regex)
    # if it failed, we can return
    if msg:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            True if len(search_from_options) == 1 else False,
            bool(msg),
            msg,
            bool(search_from), # row deletable
            no_update,
            no_update,
            n_clicks,
            no_update,
            no_update
        )

    # multiword queries add info to the dataset, the _position column. so, update this...
    # todo: this is NOT the correct way to handle this. it needs to go in session data...
    position = None
    if multiword and df is not None:
        position = json.dumps(list(df["_position"]))
    # store the search info
    indices = json.dumps(list(df["_n"]))

    filt = dict(slug=slug, user=user)
    new_value = len(SearchResult.objects.filter(**filt)) + 1

    enu = enumerate(search_from_options)
    index_for_option = next(i for i, s in enu if s["value"] == search_from) + 1

    this_search = SearchResult(
        slug=slug,
        user=user,
        idx=new_value,
        indices=indices,
        position=position,
        parent=searching_from,
        target=col,
        query=search_string,
        regex=not no_use_regex,
        inverse=skip,
        name=None,
        order=index_for_option
    )
    name = _make_search_name(this_search, corpus_size, int(lang))
    this_search.name = name
    this_search.save()

    new_option = dict(value=new_value, label=name)
    search_from_options.insert(index_for_option, new_option)

    # print("SEARCH FROM OPTIONS", len(search_from_options), search_from_options)

    helpers._update_search_result_order(search_from_options, slug, user)

    # figure out sort, filter, pagination...
    num_pages = ceil(len(df) / settings.PAGE_SIZE)
    df, _ = helpers._filter_corpus(df, filters, False)
    df, _ = helpers._sort_corpus(df, sort_by, False)
    df = helpers._correct_page(df, page_current, settings.PAGE_SIZE)
    current_cols, current_data = helpers._update_conll(df, True, conf.add_governor, slug=slug)

    return (
        current_cols,
        current_data,
        search_from_options,
        new_value,
        False,
        bool(msg),
        msg,
        True,  # row deletable, always yes
        session_clicks_clear,
        session_clicks_show,
        n_clicks,
        conll_page,
        num_pages,
    )


@app.expanded_callback(
    [
        Output("freq-table", "columns"),
        Output("freq-table", "data"),
        Output("freq-table", "editable"),
        Output("chart-from-1", "value"),
        Output("chart-from-1", "options"),
        Output("chart-from-2", "options"),
        Output("chart-from-3", "options"),
        Output("chart-from-4", "options"),
        Output("chart-from-5", "options"),
        Output("dialog-table", "displayed"),
        Output("dialog-table", "message"),
        Output("freq-table", "row_deletable"),
        Output("session-clicks-table", "data"),
        #Output("freq-table", "style_data_conditional")
    ],
    [Input("table-button", "n_clicks"), Input("freq-table", "data_previous"),],
    [
        State("freq-table", "columns"),
        State("freq-table", "data"),
        State("search-from", "value"),
        State("show-for-table", "value"),
        State("subcorpora-for-table", "value"),
        State("relative-for-table", "value"),
        State("sort-for-table", "value"),
        # State("multiindex-switch", "on"),
        # State("content-table-switch", "on"),
        State("chart-from-1", "options"),
        State("chart-from-1", "value"),
        State("session-clicks-table", "data"),
        State("session-user-id", "data"),
        State("slug", "title"),
    ],
)
def _new_table(
    n_clicks,
    prev_data,
    current_cols,
    current_data,
    search_from,
    show,
    subcorpora,
    relkey,
    sort,
    # multiindex_columns,
    # content_table,
    table_from_options,
    nv1,
    session_click_table,
    user_id,
    slug,
    **kwargs,
):
    """
    Callback when a new freq table is generated. Same logic as new_search.
    """
    delete_old_tables()

    # do nothing if not yet loaded
    if n_clicks is None:
        raise PreventUpdate

    user = User.objects.get(id=user_id)
    conf = CorpusModel.objects.get(slug=slug)

    # because no option below can return initial table, rows can now be deleted
    row_deletable = True

    # get the corpus we are tabling from
    corpus = helpers._get_corpus(slug)
    searching_from = None
    if search_from:
        uniq = dict(slug=slug, user=user, idx=search_from)
        searching_from = SearchResult.objects.get(**uniq)
        corpus = corpus.iloc[json.loads(searching_from.indices)]

    # figure out sort, subcorpora,relative and keyness
    sort = sort or "total"
    if subcorpora == "_corpus":
        subcorpora = None
    relative, keyness = helpers._translate_relative(relkey)

    # are we updating?
    # if the table making button has been clicked, we are not updating
    if session_click_table != n_clicks:
        updating = False
        session_click_table = n_clicks
    # check if table dimensions have changed
    elif prev_data is not None:
        # if number of rows has changed
        if len(prev_data) != len(current_data):
            updating = True
        # if number of columns has changed
        if len(prev_data[0]) != len(current_data[0]):
            updating = True

    # find validation errors
    msg = _table_error(show, subcorpora, updating)

    # construct the model for this table, to check if it exists
    this_table_data = dict(
        slug=slug,
        user=user,
        produced_from=searching_from,
        show=json.dumps(list(show)),
        subcorpora=json.dumps(list(subcorpora)),
        relative=relative,
        keyness=keyness
    )

    # if it exists, get its idx so we can retrieve it from user_tables
    TableResult.objects.all().delete()
    try:
        exists = TableResult.objects.get(**this_table_data)
        identifier = exists.idx
    except TableResult.DoesNotExist:
        # doesn't exist, i.e. must call .table()
        exists = None
        identifier = len(TableResult.objects.all()) + 1
        this_table_data["idx"] = identifier

    # if we are updating the table:
    if updating:
        # get the whole table from master dict of them
        table = user_tables[identifier]
        # fix columns
        table = table[[i["id"] for i in current_cols[1:]]]
        # fix rows
        print("Update table")
        print("current_data", current_data)
        print("table", table.head(5))
        correct_rows = [i[table.index.name] for i in current_data]
        table = table.loc[correct_rows]
        # store table again with same key
        user_tables[identifier] = table
    elif exists and identifier in user_tables:  # tood: second check should not be here
        msg = "Table already exists. Switching to that one to save memory."
        table = user_tables[identifier]
    # if there was a validation problem, juse use last table (?)
    elif msg:
        # todo: check
        if user_tables:
            # todo: figure this out...use current table instead?
            key, value = list(user_tables.items())[-1]
            table = user_tables[helpers._tuple_or_list(value, tuple)]
            # todo: more here?
        else:
            table = initial_tables[slug]
    else:
        # generate table
        table = corpus.table(
            show=show,
            subcorpora=subcorpora,
            relative=relative if relative != "corpus" else corpora[slug],
            keyness=keyness,
            sort=sort,
            multiindex_columns=False,  # multiindex_columns,
            show_frequencies=relative is not False and relative is not None,
        )
        # round df if floats are used
        if relative is not False or keyness:
            table = table.round(2)

        # untested
        if table.index.name == "file":
            table.index = table.index.to_series().apply(os.path.basename)
            table.index = table.index.to_series().str.replace(".conllu", "", regex=False)

        # cannot hash a corpus, which relative may be.
        # none will denote corpus as reference
        if isinstance(relative, pd.DataFrame):
            relative = None

        # then store the search information in store/freq table spaces
        user_tables[identifier] = table
        tab = TableResult(**this_table_data)
        tab.save()

    if updating:
        cols, data, style_index = no_update, no_update, no_update
    else:
        style_index = style.FILE_INDEX
        style_index["if"]["column_id"] = table.index.name
        if table.index.name in table.columns:
            print(f"Warning, {table.index.name} exists in table!")
            table = table.drop(table.index.name, axis=1)
        table = table.reset_index()
        max_row, max_col = settings.TABLE_SIZE
        tab = table.iloc[:max_row, :max_col]
        # todo: swisslaw, multi and content
        cols, data = helpers._update_frequencies(tab, True, False)

    if not msg and not updating:
        table_name = _make_table_name(search_from=search_from, **this_table_data)
        option = dict(value=identifier, label=table_name)
        table_from_options.append(option)

    return (
        cols,
        data,
        True,
        identifier,
        table_from_options,
        table_from_options,
        table_from_options,
        table_from_options,
        table_from_options,
        bool(msg),
        msg,
        row_deletable,
        session_click_table,
        #style_index
    )


@app.expanded_callback(
    [
        Output("conc-table", "columns"),
        Output("conc-table", "data"),
        Output("dialog-conc", "displayed"),
        Output("dialog-conc", "message"),
        Output("session-clicks-conc", "data"),
        Output("session-current-conc-page", "data"),
    ],
    [
        Input("update-conc", "n_clicks"),
        Input("conc-table", "page_current"),
        Input("conc-table", "sort_by"),
        Input("conc-table", "filter_query"),
    ],
    [
        State("show-for-conc", "value"),
        State("search-from", "value"),
        State("slug", "title"),
        State("session-clicks-conc", "data"),
        State("session-current-conc-page", "data"),
    ],
)
def _new_conc(
    n_clicks,
    page_current,
    sort_by,
    filter,
    show,
    search_from,
    slug,
    session_clicks_conc,
    conc_page,
    **kwargs,
):
    """
    Callback for concordance. Handles filter, sort, pagination and update
    """
    if n_clicks is None and page_current == conc_page and not sort_by and not filter:
        return [no_update] * 6

    msg = False

    if not show:
        show = "w"

    if n_clicks and not search_from and show != "w":
        msg = "You cannot concordance an entire corpus. Please do a search first."
        return no_update, no_update, bool(msg), msg, n_clicks, page_current

    if not search_from and show == "w":
        conc = initial_concs[slug]
    else:
        session_search = None #todo
        specs, corpus = helpers._get_specs_and_corpus(search_from, session_search, corpora, slug)
        met = ["file", "s", "i"]
        if isinstance(corpus, pd.DataFrame):
            for feat in {"speaker", "year"}:
                if feat in corpus.columns:
                    met.append(feat)

        conc = corpus.conc(show=show, metadata=met, window=(100, 100), n=settings.MAX_CONC)
        conc = helpers._add_links(conc, slug=slug, conc=True)
        conc["file"] = conc["file"].apply(os.path.basename)
        conc["file"] = conc["file"].str.replace(".conllu", "", regex=False)

    # if just changing page
    if conc_page != page_current:
        corpus_size = len(conc)
        conc = helpers._correct_page(conc, page_current, settings.PAGE_SIZE)
        cols, data = helpers._update_concordance(conc, True)
        return cols, data, bool(msg), msg, n_clicks, page_current

    # yes, these are named corpus, but they are fine on conc as well
    conc, corpus_sorted = helpers._sort_corpus(conc, sort_by, False)
    conc, corpus_filtered = helpers._filter_corpus(conc, filter, False)
    conc = helpers._correct_page(conc, page_current, settings.PAGE_SIZE)
    cols, data = helpers._update_concordance(conc, deletable=True)
    return cols, data, bool(msg), msg, n_clicks, page_current


@app.expanded_callback(
    [Output("matching-text", "children"), Output("skip-switch", "className")],
    [Input("skip-switch", "on")],
)
def _matching_not_matching(on, **kwargs):
    """
    Change the text for matching/not matching
    """
    text = "matching" if not on else "not matching"
    classname = "colour-off" if not on else "colour-on"
    return text, classname


@app.expanded_callback(
    [Output("regex-text", "children"), Output("use-regex", "className")],
    [Input("use-regex", "on")],
)
def _use_regex(on, **kwargs):
    """
    Colour and change the text for simple/regex search
    """
    text = "simple search" if not on else "regular expression"
    classname = "colour-off" if not on else "colour-on"
    return text, classname


@app.expanded_callback(
    [Output("multiindex-switch", "disabled"), Output("multiindex-switch", "on")],
    [Input("multiindex-switch", "n_clicks"), Input("show-for-table", "value")],
    [State("multiindex-switch", "on")],
)
def _multiindex(_, show, on, **kwargs):
    """
    Multiindexing --- disabled currently
    """
    if not show or len(show) < 2:
        return True, False
    return False, on


@app.expanded_callback(
    [Output("language-text", "children"), Output("language-switch", "className")],
    [Input("language-switch", "on")],
)
def _switch_language(on, **kwargs):
    """
    Switch the text of the active language
    """
    text = "English" if not on else "German"
    classname = "colour-off" if not on else "colour-on"
    return text, classname


language_outputs = [Output(c, f) for c, f in sorted(LANGUAGES) if f]
language_states = [State(c, f) for c, f in sorted(LANGUAGES) if f]


@app.expanded_callback(
    language_outputs, [Input("language-switch", "on")], language_states,
)
def _change_language(lang, *args, **kwargs):
    """
    Change the language of the entire explorer
    """
    if lang is None:
        return no_update
    return [v[int(lang)] for (_, f), v in sorted(LANGUAGES.items()) if f]
