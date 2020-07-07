"""
buzzword explorer: build the explore page and its tabs
"""
import json

import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
from buzz.constants import SHORT_TO_COL_NAME
from buzz.corpus import Corpus

from . import style
from .chart import CHART_TYPES, _df_to_figure
from .helpers import _drop_cols_for_datatable, _get_cols, _update_frequencies
from .strings import _capitalize_first, _make_search_name, _make_table_name

from django.conf import settings


DAQ_THEME = {
    "dark": False,
    "detail": "#007439",
    "primary": "#a32424",  # button when switched 'on' / not matching
    "secondary": "#44ad78",  # bottom off / matching
}


def _make_storage(configs):
    """
    Invisible containers that store session info
    """
    # user storage for searches, tables, and click counts
    search_store = dcc.Store(id="session-search", data=dict())
    tables_store = dcc.Store(id="session-tables", data=dict())
    click_clear = dcc.Store(id="session-clicks-clear", data=-1)
    click_show = dcc.Store(id="session-clicks-show", data=-1)
    click_table = dcc.Store(id="session-clicks-table", data=-1)
    configs = dcc.Store(id="session-configs", data=configs)
    content = html.Div(id="page-content")
    stores = [search_store, tables_store, click_clear, click_show, click_table, configs]
    return html.Div(stores + [content])


def _build_dataset_space(df, config):
    """
    Build the search interface and the conll display
    """
    if isinstance(df, Corpus):
        df = df.files[0].load()
    cols = _get_cols(df, config["add_governor"])
    extra = [("Dependencies", "d"), ("Describe thing", "describe")]
    grams = [("Match (default)", 0), ("Bigrams of match", 1), ("Trigrams of match", 2)]
    extra = [dict(label=l, value=v) for l, v in extra]
    grams = [dict(label=l, value=v) for l, v in grams]
    cols = extra + cols
    df = _drop_cols_for_datatable(df, config["add_governor"])
    df = df.reset_index()
    # no file extensions
    df["file"] = df["file"].str.replace(".txt.conllu", "", regex=False)
    max_row, max_col = config["table_size"]
    df = df.iloc[:max_row, :max_col]
    pieces = [
        dcc.Dropdown(
            id="search-target",
            options=cols,
            value="w",
            # title="Select the column you wish to search (e.g. word/lemma/POS) "
            # + ", or query language (e.g. Tgrep2, Depgrep)",
            style={"width": "200px", "fontFamily": "monospace", **style.NEAR_FRONT},
        ),
        # the matching/not matching button and its text
        html.Div(
            id="matching-box",
            children=[
                daq.BooleanSwitch(
                    theme=DAQ_THEME,
                    className="colour-off",
                    id="skip-switch",
                    on=False,
                    style={"verticalAlign": "top", **style.MARGIN_5_MONO},
                ),
                html.Div(
                    id="matching-text",
                    style={"verticalAlign": "bottom", **style.MARGIN_5_MONO},
                ),
            ],
        ),
        dcc.Input(
            id="input-box",
            type="text",
            placeholder="Enter regular expression search query...",
            size="60",
            style=style.MARGIN_5_MONO,
        ),
        html.Div(
            id="regex-box",
            children=[
                daq.BooleanSwitch(
                    theme=DAQ_THEME,
                    className="colour-off",
                    id="use-regex",
                    on=False,
                    style={"verticalAlign": "top", **style.MARGIN_5_MONO},
                ),
                html.Div(
                    id="regex-text",
                    style={"verticalAlign": "bottom", **style.MARGIN_5_MONO},
                ),
            ],
        ),
        dcc.Dropdown(
            id="gram-select",
            options=grams,
            # value="",
            placeholder="What to return from search",
            disabled=False,
            style={"width": "240px", "fontFamily": "monospace", **style.FRONT},
        ),
        html.Button("Search", id="search-button"),
    ]
    pieces = [html.Div(piece, style=style.CELL_MIDDLE_35) for piece in pieces]

    search_space = html.Div(
        pieces, style={"fontFamily": "bold", **style.VERTICAL_MARGINS}
    )
    columns = [
        {
            "name": _capitalize_first(SHORT_TO_COL_NAME.get(i, i)).replace("_", " "),
            "id": i,
            "deletable": False,
            "hideable": True,
        }
        for i in df.columns
    ]
    data = df.to_dict("rows")

    conll_table = dash_table.DataTable(
        id="conll-view",
        columns=columns,
        data=data,
        editable=True,
        style_cell={**style.HORIZONTAL_PAD_5, **{"minWidth": "60px"}},
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_deletable=False,
        selected_rows=[],
        page_action="none",
        page_current=0,
        page_size=config["page_size"],
        # style_as_list_view=True,
        virtualization=True,
        style_table={"maxHeight": "1000px"},
        fixed_rows={"headers": True, "data": 0},
        style_header=style.BOLD_DARK,
        style_cell_conditional=style.LEFT_ALIGN,
        style_data_conditional=style.INDEX + style.STRIPES,
        merge_duplicate_headers=True,
        export_format="xlsx",
        export_headers="display",
    )
    # add loading
    conll_table = dcc.Loading(
        type="default",
        id="loading-main",
        fullscreen=True,
        className="loading-main",
        children=[conll_table],
    )
    div = html.Div(id="dataset-container", children=[search_space, conll_table])
    return html.Div(id="display-dataset", children=[div])


def _build_frequencies_space(corpus, table, config):
    """
    Build stuff related to the frequency table
    """
    cols = _get_cols(corpus, config["add_governor"])
    show_check = dcc.Dropdown(
        placeholder="Features to show",
        multi=True,
        id="show-for-table",
        options=cols,
        value=[],
        style={**style.MARGIN_5_MONO, **style.FRONT},
    )
    show_check = html.Div(show_check, style=style.TSTYLE)
    subcorpora_drop = dcc.Dropdown(
        id="subcorpora-for-table",
        options=[dict(value="_corpus", label="Entire corpus")] + cols,
        placeholder="Feature for index",
        style={**style.MARGIN_5_MONO, **style.FRONT},
    )
    subcorpora_drop = html.Div(subcorpora_drop, style=style.TSTYLE)
    relative_drop = dcc.Dropdown(
        id="relative-for-table",
        style={**style.MARGIN_5_MONO, **style.NEAR_FRONT},
        options=[
            {"label": "Absolute frequency", "value": "ff"},
            {"label": "Relative of result", "value": "tf"},
            {"label": "Relative of corpus", "value": "nf"},
            {"label": "Keyness: log likelihood", "value": "fl"},
            {"label": "Keyness: percent difference", "value": "fp"},
        ],
        placeholder="Relative/keyness calculation",
    )
    relative_drop = html.Div(relative_drop, style=style.TSTYLE)
    sort_drop = dcc.Dropdown(
        id="sort-for-table",
        style={**style.MARGIN_5_MONO, **style.NEAR_FRONT},
        options=[
            {"label": "Total", "value": "total"},
            {"label": "Infrequent", "value": "infreq"},
            {"label": "Alphabetical", "value": "name"},
            {"label": "Reverse-alphabetical", "value": "reverse"},
            {"label": "Increasing", "value": "increase"},
            {"label": "Decreasing", "value": "decrease"},
            {"label": "Static", "value": "static"},
            {"label": "Turbulent", "value": "turbulent"},
        ],
        placeholder="Sort columns by...",
    )
    sort_drop = html.Div(sort_drop, style=style.TSTYLE)
    max_row, max_col = config["table_size"]
    print(f"Making {max_row}x{max_col} table for {config['corpus_name']} ...")
    table = table.iloc[:max_row, :max_col]
    columns, data = _update_frequencies(table, False, False)
    print("Done!")

    # modify the style_index used for other tables to just work for this index
    style_index = style.FILE_INDEX
    style_index["if"]["column_id"] = table.index.name
    freq_table = dcc.Loading(
        type="default",
        children=[
            dash_table.DataTable(
                id="freq-table",
                columns=columns,
                data=data,
                editable=False,
                style_cell={
                    **style.HORIZONTAL_PAD_5,
                    **{"maxWidth": "145px", "minWidth": "60px"},
                },
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                row_deletable=False,
                selected_rows=[],
                page_current=0,
                page_size=config["page_size"],
                page_action="none",
                fixed_rows={"headers": True, "data": 0},
                virtualization=True,
                style_table={"maxHeight": "1000px"},
                style_header=style.BOLD_DARK,
                style_cell_conditional=style.LEFT_ALIGN,
                style_data_conditional=[style_index] + style.STRIPES,
                merge_duplicate_headers=True,
                export_format="xlsx",
                export_headers="display",
            )
        ],
    )

    sty = {"width": "20%", **style.CELL_MIDDLE_35, **style.MARGIN_5_MONO}

    multi = html.Span(
        children=[
            daq.BooleanSwitch(
                theme=DAQ_THEME,
                id="multiindex-switch",
                on=False,
                disabled=True,
                style={**style.MARGIN_5_MONO, **style.TSTYLE},
            ),
            html.Div(
                children="Multicolumn mode",
                id="multiindex-text",
                style={
                    **style.MARGIN_5_MONO,
                    **style.TSTYLE,
                    **{"whiteSpace": "nowrap"},
                },
            ),
        ],
        style={**style.CELL_MIDDLE_35, **style.TSTYLE},
    )
    content = html.Span(
        children=[
            daq.BooleanSwitch(
                theme={**DAQ_THEME, **{"primary": "#47d153"}},
                id="content-table-switch",
                on=False,
                style={**style.MARGIN_5_MONO, **style.TSTYLE},
            ),
            html.Div(
                children="Show content, not frequency",
                style={**style.MARGIN_5_MONO, **style.TSTYLE},
            ),
        ],
        style={**style.CELL_MIDDLE_35, **style.TSTYLE},
    )

    gen = "Generate table"
    generate = html.Button(gen, id="table-button", style=sty)
    top = html.Div([show_check, subcorpora_drop, multi, content])
    bottom = html.Div([sort_drop, relative_drop, generate])
    toolbar = html.Div([top, bottom], style=style.VERTICAL_MARGINS)
    div = html.Div([toolbar, freq_table])
    return html.Div(id="display-frequencies", children=[div])


def _build_concordance_space(df, config):
    """
    Div representing the concordance tab
    """
    if isinstance(df, Corpus):
        df = df.files[0].load()
    cols = _get_cols(df, config["add_governor"])
    show_check = dcc.Dropdown(
        multi=True,
        placeholder="Features to show",
        id="show-for-conc",
        options=cols,
        style={**style.MARGIN_5_MONO, **style.NEAR_FRONT},
    )
    update = html.Button("Update", id="update-conc", style=style.MARGIN_5_MONO)
    tstyle = dict(width="100%", **style.CELL_MIDDLE_35)
    toolbar = [html.Div(i, style=tstyle) for i in [show_check, update]]
    conc_space = html.Div(toolbar, style=style.VERTICAL_MARGINS)

    # todo, not respected for some reason?
    max_row, max_col = config["table_size"]
    max_conc = config.get("max_conc", -1)

    meta = ["file", "s", "i"]
    if "speaker" in df.columns:
        meta.append("speaker")

    # do an initial search, potentially from corpora.json
    # default to, get nouns
    if config.get("initial_query"):
        query = json.loads(config["initial_query"])
    else:
        query = {"target": "x", "query": "NOUN"}

    print(f"Making concordance (max {max_conc}) for {config['corpus_name']} ...")
    df = getattr(df.just, query["target"])(query["query"])
    df = df.conc(metadata=meta, window=(100, 100), n=max_conc)
    print("Done!")

    just = ["left", "match", "right", "file", "s", "i"]
    if "speaker" in df.columns:
        just.append("speaker")
    df = df[just]
    columns = [
        {
            "name": _capitalize_first(SHORT_TO_COL_NAME.get(i, i)),
            "id": i,
            "deletable": i not in ["left", "match", "right"],
            "hideable": True,
        }
        for i in df.columns
    ]
    style_data = [style.STRIPES[0], style.INDEX[0]] + style.CONC_LMR
    data = df.to_dict("rows")
    rule = (
        "display: inline; white-space: inherit; "
        + "overflow: inherit; text-overflow: inherit;"
    )
    conc = dcc.Loading(
        type="default",
        children=[
            dash_table.DataTable(
                id="conc-table",
                css=[{"selector": ".dash-cell div.dash-cell-value", "rule": rule}],
                columns=columns,
                data=data,
                editable=True,
                style_cell={**style.HORIZONTAL_PAD_5, **{"minWidth": "60px"}},
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                row_deletable=True,
                selected_rows=[],
                page_action="none",
                fixed_rows={"headers": True, "data": 0},
                page_current=0,
                page_size=config["page_size"],
                virtualization=True,
                style_table={"maxHeight": "1000px"},
                style_as_list_view=True,
                style_header=style.BOLD_DARK,
                style_cell_conditional=style.LEFT_ALIGN_CONC,
                style_data_conditional=style_data,
                merge_duplicate_headers=True,
                export_format="xlsx",
                export_headers="display",
            )
        ],
    )

    div = html.Div([conc_space, conc])
    return html.Div(id="display-concordance", children=[div])


def _build_chart_space(table, config):
    """
    Div representing the chart tab
    """
    charts = []
    for chart_num, kind in [
        (1, "stacked_bar"),
        (2, "line"),
        (3, "area"),
        (4, "heatmap"),
        (5, "bar"),
    ]:

        table_from = [dict(value=0, label=_make_table_name("initial"))]
        dropdown = dcc.Dropdown(
            id=f"chart-from-{chart_num}",
            options=table_from,
            value=0,
            style=style.MARGIN_5_MONO,
        )
        types = [
            dict(label=_capitalize_first(i).replace("_", " "), value=i)
            for i in sorted(CHART_TYPES)
        ]
        chart_type = dcc.Dropdown(
            id=f"chart-type-{chart_num}",
            options=types,
            value=kind,
            style=style.MARGIN_5_MONO,
        )
        transpose = daq.BooleanSwitch(
            theme=DAQ_THEME,
            id=f"chart-transpose-{chart_num}",
            on=False,
            style={"verticalAlign": "middle"},
        )
        top_n = dcc.Input(
            id=f"chart-top-n-{chart_num}",
            placeholder="Results to plot",
            type="number",
            min=1,
            max=99,
            value=7,
            style=style.MARGIN_5_MONO,
        )
        update = html.Button("Update", id=f"figure-button-{chart_num}")

        toolbar = [dropdown, chart_type, top_n, transpose, update]
        widths = {
            dropdown: "65%",
            chart_type: "25%",
            top_n: "3%",
            transpose: "4%",
            update: "13%",
        }
        tools = list()
        for component in toolbar:
            width = widths.get(component, "10%")
            nstyle = {**style.CELL_MIDDLE_35, **{"width": width}}
            div = html.Div(component, style=nstyle)
            if component == transpose:
                div.title = "Transpose axes"
            elif component == top_n:
                div.title = "Number of entries to display"
            tools.append(div)
        toolbar = html.Div(tools, style=style.VERTICAL_MARGINS)
        figure = _df_to_figure(table, kind=kind)
        chart_data = dict(
            id=f"chart-{chart_num}",
            figure=figure,
            style={"height": "60vh", "width": "95vw"},
        )
        chart = dcc.Loading(type="default", children=[dcc.Graph(**chart_data)])
        chart_space = html.Div([toolbar, chart])
        name = f"Chart #{chart_num}"
        summary = html.Summary(name, style=style.CHART_SUMMARY)
        drop = [summary, html.Div(chart_space)]
        collapse = html.Details(drop, open=chart_num == 1)
        charts.append(collapse)
    div = html.Div(charts)
    return html.Div(id="display-chart", children=[div])


def make_explore_page(corpus, table, config, configs):
    """
    Create every tab, as well as the top rows of stuff, and tab container

    Return html.Div
    """
    slug = html.Div(id="slug", title=config["slug"], style={"display": "none"})
    dataset = _build_dataset_space(corpus, config)
    frequencies = _build_frequencies_space(corpus, table, config)
    chart = _build_chart_space(table, config)
    concordance = _build_concordance_space(corpus, config)
    label = _make_search_name(config["corpus_name"], config["length"], dict())
    search_from = [dict(value=0, label=label)]
    show = html.Button(
        "Show", id="show-this-dataset", style={**style.MARGIN_5_MONO, **style.FRONT}
    )
    show.title = "Show the selected corpus or search result in the Dataset tab"
    clear = html.Button("Clear history", id="clear-history", style=style.MARGIN_5_MONO)
    clear.title = "Delete all searches and frequency tables"

    dropdown = dcc.Dropdown(
        id="search-from", options=search_from, value=0, disabled=True
    )

    drop_style = {
        "fontFamily": "monospace",
        "width": "50%",
        **style.HORIZONTAL_PAD_5,
        **style.BLOCK_MIDDLE_35,
        **style.FRONT,
    }
    # remove the paddingTop, which is not needed in explore view
    nav = {k: v for k, v in style.NAV_HEADER.items() if k != "paddingTop"}

    top_bit = [
        html.Img(
            src="../../static/bolt.jpg",
            height=42,
            width=38,
            style=style.BLOCK_MIDDLE_35,
        ),
        #todo: this button doesn't work!?
        dcc.Link("buzzword", href="/", style=nav),
        # these spaces are used to flash messages to the user if something is wrong
        dcc.ConfirmDialog(id="dialog-search", message=""),
        dcc.ConfirmDialog(id="dialog-table", message=""),
        dcc.ConfirmDialog(id="dialog-chart", message=""),
        dcc.ConfirmDialog(id="dialog-conc", message=""),
        html.Div(dropdown, style=drop_style),
        html.Div(show, style=dict(width="10%", **style.BLOCK_MIDDLE_35)),
        html.Div(clear, style=dict(width="10%", **style.BLOCK_MIDDLE_35)),
    ]
    top_bit = html.Div(top_bit, style=style.VERTICAL_MARGINS)

    tab_headers = dcc.Tabs(
        id="tabs",
        value="dataset",
        style={
            "lineHeight": 0,
            "fontFamily": "monospace",
            "font": "12px Arial",
            "fontWeight": 600,
            "color": "#555555",
            "paddingLeft": "10px",
            "paddingRight": "10px",
        },
        children=[
            dcc.Tab(label="DATASET", value="dataset"),
            dcc.Tab(label="FREQUENCIES", value="frequencies"),
            dcc.Tab(label="CHART", value="chart"),
            dcc.Tab(label="CONCORDANCE", value="concordance"),
        ],
    )
    blk = {"display": "block", **style.HORIZONTAL_PAD_5}
    conll_display = html.Div(id="display-dataset", children=[dataset])
    hide = {"visibility": "hidden"}

    tab_contents = [
        html.Div(
            children=[
                html.Div(id="tab-dataset", style=blk, children=[conll_display]),
                html.Div(id="tab-frequencies", style=hide, children=[frequencies]),
                html.Div(id="tab-chart", style=hide, children=[chart]),
                html.Div(id="tab-concordance", style=hide, children=[concordance]),
            ]
        )
    ]

    pad = {"paddingLeft": "10px", "paddingRight": "10px"}
    tab_contents = html.Div(id="tab-contents", children=tab_contents)
    children = [slug, _make_storage(configs), top_bit, tab_headers, tab_contents]
    return html.Div(id="everything", children=children, style=pad)
