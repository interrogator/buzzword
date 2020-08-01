"""
buzzword explorer: build the explore page and its tabs
"""
import json
import os

import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
from buzz.constants import SHORT_TO_COL_NAME
from buzz.corpus import Corpus

from explore.models import Corpus as CorpusModel

from . import style
from .chart import CHART_TYPES, _df_to_figure
from .helpers import _drop_cols_for_datatable, _get_cols, _update_frequencies, _add_links
from .strings import _capitalize_first, _make_search_name, _make_table_name

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .lang import LANGUAGES

from math import ceil


DAQ_THEME = {
    "dark": False,
    "detail": "#007439",
    "primary": "#a32424",  # button when switched 'on' / not matching
    "secondary": "#44ad78",  # bottom off / matching
}


def _make_storage():
    """
    Invisible containers that store session info
    """
    # user storage for searches, tables, and click counts
    search_store = dcc.Store(id="session-search", data=dict())
    tables_store = dcc.Store(id="session-tables", data=dict())
    click_clear = dcc.Store(id="session-clicks-clear", data=-1)
    click_show = dcc.Store(id="session-clicks-show", data=-1)
    click_search = dcc.Store(id="session-clicks-search", data=-1)
    click_conc = dcc.Store(id="session-clicks-conc", data=-1)
    click_table = dcc.Store(id="session-clicks-table", data=-1)
    conll_page = dcc.Store(id="session-current-conll-page", data=0)
    conc_page = dcc.Store(id="session-current-conc-page", data=0)
    content = html.Div(id="page-content")
    stores = [search_store, tables_store, click_clear, click_show, click_search, click_conc, click_table, conll_page, conc_page]
    return html.Div(stores + [content])


def _build_dataset_space(df, config):
    """
    Build the search interface and the conll display
    """
    if isinstance(df, Corpus):
        df = df.files[0].load()
    cols = _get_cols(df, config.add_governor)
    extra = [("Dependencies", "d"), ("Describe thing", "describe")]
    grams = [("Match (default)", 0), ("Bigrams of match", 1), ("Trigrams of match", 2)]
    extra = [dict(label=l, value=v) for l, v in extra]
    grams = [dict(label=l, value=v) for l, v in grams]
    cols = extra + cols
    df = _drop_cols_for_datatable(df, config.add_governor)
    df = df.reset_index()
    corpus_size = len(df)
    df = df.iloc[:settings.PAGE_SIZE]
    # no file extensions
    df["file"] = df["file"].str.replace(".conllu", "", regex=False)
    df["file"] = df["file"].str.replace("^.*/conllu/", "", regex=True)
    max_row, max_col = settings.TABLE_SIZE
    if max_row:
        df = df.iloc[:max_row]
    if max_col:
        df = df.iloc[:,:max_col]
    if config.pdfs:
        df = _add_links(df, slug=config.slug, conc=False)
    pieces = [
        dcc.Dropdown(
            id="search-target",
            options=cols,
            value="w",
            # title="Select the column you wish to search (e.g. word/lemma/POS) "
            # + ", or query language (e.g. Tgrep2, Depgrep)",
            style={"width": "200px", "fontFamily": "monospace"},
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
            placeholder="Enter search query...",
            size="60",
            style=style.MARGIN_5_MONO,
            className="input-lg form-control"
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
                    style={"textAlign": "center", "verticalAlign": "bottom", "width": "140px", **style.MARGIN_5_MONO},
                ),
            ],
        ),
        #dcc.Dropdown(
        #    id="gram-select",
        #    options=grams,
        #    # value="",
        #    placeholder="What to return from search",
        #    disabled=False,
        #    style={"width": "240px", "fontFamily": "monospace", **style.FRONT},
        #),
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
            "presentation": ("markdown" if i == "file" else None)
        }
        for i in df.columns
    ]
    data = df.to_dict("rows")

    conll_table = dash_table.DataTable(
        id="conll-view",
        columns=columns,
        data=data,
        # editable=True,
        style_cell={**style.HORIZONTAL_PAD_5, **{"minWidth": "60px"}},
        filter_action="custom",
        sort_action="custom",
        sort_mode="multi",
        sort_by=[],
        row_deletable=False,
        selected_rows=[],
        page_action="custom",
        page_current=0,
        page_size=settings.PAGE_SIZE,
        page_count=ceil(corpus_size/settings.PAGE_SIZE),
        # style_as_list_view=True,
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        # virtualization=True,
        # style_table={},
        fixed_rows={"headers": True, "data": 0},
        style_header=style.BOLD_DARK,
        style_cell_conditional=style.LEFT_ALIGN,
        style_data_conditional=style.INDEX + style.STRIPES,
        merge_duplicate_headers=True,
        #export_format="xlsx",
        #export_headers="display",
    )
    # add loading
    conll_table = dcc.Loading(
        type="default",
        id="loading-main",
        fullscreen=True,
        className="loading-main",
        children=conll_table,
    )
    data_space = html.Div([search_space, conll_table])
    div = html.Div(id="dataset-container", children=data_space)
    return html.Div(id="display-dataset-1", children=[div])


def _build_frequencies_space(corpus, table, config):
    """
    Build stuff related to the frequency table
    """
    cols = _get_cols(corpus, config.add_governor)
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
    relative_drop = html.Div(relative_drop, style={**style.TSTYLE, **{"width": "21%"}})
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
    max_row, max_col = settings.TABLE_SIZE
    print(f"Making {max_row}x{max_col} table for {config.name} ...")
    table = table.iloc[:100, :100]

    style_index = style.FILE_INDEX
    style_index["if"]["column_id"] = "year"
    index_name = table.index.name

    table = table.reset_index()

    if "file" in table.columns:
        table["file"] = table["file"].apply(os.path.basename)
        table["file"] = table["file"].str.rstrip(".conllu")
        try:
            table = _add_links(table, slug=config.slug, conc=False)
        except ObjectDoesNotExist:
            pass

    columns, data = _update_frequencies(table, False, False)
    print("Done!")

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
                page_size=20,
                page_action="native",
                fixed_rows={"headers": True, "data": 0},
                #virtualization=True,
                #style_table={"overflowY": "scroll", "overflowX": "hidden"},
                style_header=style.BOLD_DARK,
                style_cell_conditional=style.LEFT_ALIGN,
                style_data_conditional=[{"if": {"column_id": index_name},
                                            "backgroundColor": "#fafafa",
                                            "color": "#555555",
                                            "fontWeight": "bold",
                                            "width": "20%",
                                        }] + style.STRIPES,
                merge_duplicate_headers=True,
                #export_format="xlsx",
                #export_headers="display",
                css=[{"selector": ".show-hide", "rule": "display: none"}],
            )
        ],
    )

    sty = {"width": "22%", **style.CELL_MIDDLE_35, **style.MARGIN_5_MONO}

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
    # disabled in swisslaw
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
    generate = html.Button(gen, id="table-button", style={**style.MARGIN_5_MONO, **style.TSTYLE})
    top = html.Div([show_check, subcorpora_drop, sort_drop, relative_drop, generate]) # multi, content
    #bottom = html.Div([sort_drop, relative_drop, generate])
    toolbar = html.Div([top], style=style.VERTICAL_MARGINS) # , bottom
    div = html.Div([toolbar, freq_table])
    return html.Div(id="display-frequencies", children=[div])


def _build_concordance_space(df, conc, config, slug):
    """
    Div representing the concordance tab
    """
    cols = _get_cols(df, config.add_governor)
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

    num_conc = len(conc)
    max_row, max_col = settings.TABLE_SIZE
    max_conc = settings.MAX_CONC
    conc = conc.iloc[:settings.PAGE_SIZE]

    columns = [
        {
            "name": _capitalize_first(SHORT_TO_COL_NAME.get(i, i)),
            "id": i,
            "deletable": i not in ["left", "match", "right"],
            "hideable": True,
            "presentation": ("markdown" if i == "match" else None)
        }
        for i in conc.columns
    ]
    style_data = [style.STRIPES[0], style.INDEX[0]] + style.CONC_LMR
    data = conc.to_dict("rows")
    rule = (
        "display: inline; white-space: inherit; "
        + "overflow: inherit; text-overflow: inherit;"
    )
    conc = dcc.Loading(
        type="default",
        children=[
            dash_table.DataTable(
                id="conc-table",
                css=[{"selector": ".dash-cell div.dash-cell-value", "rule": rule}, {"selector": ".show-hide", "rule": "display: none"}],
                columns=columns,
                data=data,
                editable=True,
                style_cell={**style.HORIZONTAL_PAD_5, **{"minWidth": "60px"}},
                filter_action="custom",
                sort_action="custom",
                sort_mode="multi",
                row_deletable=True,
                selected_rows=[],
                page_action="custom",
                fixed_rows={"headers": True, "data": 0},
                page_current=0,
                page_size=settings.PAGE_SIZE,
                page_count=ceil(num_conc/settings.PAGE_SIZE),
                #virtualization=True,
                # style_table={"overflow": "hidden"},
                style_as_list_view=True,
                style_header=style.BOLD_DARK,
                style_cell_conditional=style.LEFT_ALIGN_CONC,
                style_data_conditional=style_data,
                merge_duplicate_headers=True,
                #export_format="xlsx",
                #export_headers="display",
            )
        ],
    )

    div = html.Div([conc_space, conc])
    return html.Div(id="display-concordance", children=[div])


def _build_chart_space(table, iterate_over=None, width="95vw", no_from_select=False, height="60vh"):
    """
    Div representing the chart tab
    """
    charts = []
    iterate_over = iterate_over or [
        (1, "stacked_bar"),
        (2, "line"),
        (3, "area"),
        (4, "heatmap"),
        (5, "bar"),
    ]

    for chart_num, kind in iterate_over:
        table_from = [dict(value=0, label=_make_table_name("initial"))]
        if not no_from_select:
            dropdown = dcc.Dropdown(
                id=f"chart-from-{chart_num}",
                options=table_from,
                value=0,
                style=style.MARGIN_5_MONO,
            )
        else:
            dropdown = html.Div("", style={"display": "none"})
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
            style={"verticalAlign": "middle", "marginLeft": "10px", "marginRight": "10px"},
        )
        top_n = dcc.Input(
            id=f"chart-top-n-{chart_num}",
            placeholder="Results to plot",
            type="number",
            min=1,
            max=99,
            value=7,
            style={**style.MARGIN_5_MONO, **{"marginRight": "20px"}},
            className="form-control input-lg"
        )
        update = html.Button("Update", id=f"figure-button-{chart_num}")

        toolbar = [dropdown, chart_type, top_n, transpose, update]
        widths = {
            dropdown: "60%" if not no_from_select else "0%",
            chart_type: "25%",
            top_n: "8%",
            transpose: "4%",
            update: "13%",
        }
        tools = list()
        for component in toolbar:
            this_width = widths.get(component, "10%")
            nstyle = {**style.CELL_MIDDLE_35, **{"width": this_width}}
            div = html.Div(component, style=nstyle)
            if component == transpose:
                div.title = "Transpose axes"
            elif component == top_n:
                div.title = "Number of entries to display"
            tools.append(div)
        toolbar = html.Div(tools, style=style.VERTICAL_MARGINS, className="chart-toolbar")
        figure = _df_to_figure(table, kind=kind)
        chart_data = dict(
            id=f"chart-{chart_num}",
            figure=figure,
            style={"height": height, "width": width},
        )
        chart = dcc.Loading(type="default", id=f"chart-holder-{chart_num}", children=[dcc.Graph(**chart_data)])
        chart_space = html.Div([toolbar, chart])
        name = f"Chart #{chart_num}"
        summary = html.Summary(name, id=f"chart-num-{chart_num}", style=style.CHART_SUMMARY)
        drop = [summary, html.Div(chart_space)]
        collapse = html.Details(drop, open=chart_num == 1)
        charts.append(collapse)
    div = html.Div(charts)
    return html.Div(id="display-chart", children=[div])


def make_explore_page(corpus, table, conc, slug, spec=False):
    """
    Create every tab, as well as the top rows of stuff, and tab container

    Return html.Div
    """
    config = CorpusModel.objects.get(slug=slug)
    slug_div = html.Div(id="slug", title=slug, style={"display": "none"})
    dataset = _build_dataset_space(corpus, config)
    frequencies = _build_frequencies_space(corpus, table, config)
    chart = _build_chart_space(table)
    concordance = _build_concordance_space(corpus, conc, config, slug)
    print(f"Corpus length (debug) {len(corpus)}")
    label = _make_search_name(config.name, len(corpus), dict(), 0)  # 0 == english
    search_from = [dict(value=0, label=label)]
    show = html.Button("Show", id="show-this-dataset", style=style.MARGIN_5_MONO)
    show.title = "Show the selected corpus or search result in the Dataset tab"
    clear = html.Button("Clear history", id="clear-history", style=style.MARGIN_5_MONO)
    langselect = html.Div(
        id="langselect-box",
        children=[
            daq.BooleanSwitch(
                theme=DAQ_THEME,
                className="colour-off",
                id="language-switch",
                on=False, # false == en, true == de; get from user model
                style={"verticalAlign": "top", **style.MARGIN_5_MONO},
            ),
            html.Div(
                id="language-text",
                style={"verticalAlign": "bottom", "textAlign": "center", **style.MARGIN_5_MONO},
            ),
        ],
        style={"marginRight": "20px"}
    )
    clear.title = "Delete all searches and frequency tables"
    langselect.title = "Select language for the interface"

    dropdown = dcc.Dropdown(
        id="search-from", options=search_from, value=0, disabled=True
    )

    drop_style = {
        "fontFamily": "monospace",
        "width": "50%",
        **style.HORIZONTAL_PAD_5,
        **style.BLOCK_MIDDLE_35,
        **style.NEAR_FRONT,
    }
    # remove the paddingTop, which is not needed in explore view
    nav = {k: v for k, v in style.NAV_HEADER.items() if k != "paddingTop"}

    mainlink = "/" if not spec else f"/{slug}"
    img = html.Img(
        src="../../static/bolt.jpg",
        height=42,
        width=38,
        style=style.BLOCK_MIDDLE_35
    )
    top_bit = [
        html.A(["buzzword", img], href=mainlink, style=nav),
        # these spaces are used to flash messages to the user if something is wrong
        dcc.ConfirmDialog(id="dialog-search", message=""),
        dcc.ConfirmDialog(id="dialog-table", message=""),
        dcc.ConfirmDialog(id="dialog-chart", message=""),
        dcc.ConfirmDialog(id="dialog-conc", message=""),
        html.Div(dropdown, style=drop_style),
        html.Div(show, style=dict(width="10%", **style.BLOCK_MIDDLE_35)),
        html.Div(clear, style=dict(width="10%", **style.BLOCK_MIDDLE_35)),
        html.Div(langselect, style=dict(**style.BLOCK_MIDDLE_35, **{"float": "right", "marginRight": "10px"})),
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
            dcc.Tab(id="dataset-tab-label", label="DATASET", value="dataset"),
            dcc.Tab(id="freq-tab-label", label="FREQUENCIES", value="frequencies"),
            dcc.Tab(id="chart-tab-label", label="CHART", value="chart"),
            dcc.Tab(id="conc-tab-label", label="CONCORDANCE", value="concordance"),
        ],
    )
    blk = {"display": "block", **style.HORIZONTAL_PAD_5}
    conll_display = html.Div(id="display-dataset", children=[dataset])
    hide = {"display": "none"}

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
    children = [slug_div, _make_storage(), top_bit, tab_headers, tab_contents]
    return html.Div(id="everything", children=children, style=pad)
