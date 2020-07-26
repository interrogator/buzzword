# flake8: noqa

import json
import os

import dash
from dash import no_update
import dash_core_components as dcc
import dash_html_components as html

from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output, State
import dash_table

from django.conf import settings

from buzz.constants import SHORT_TO_COL_NAME
from explorer.strings import _capitalize_first
from explorer.helpers import _get_corpus
from explorer.chart import _df_to_figure
from explorer import style


def _make_layout():
    path = f"static/{settings.BUZZWORD_SPECIFIC_CORPUS}/example.json"
    with open(path) as fo:
        text = json.load(fo)

    try:
        corpus = _get_corpus(settings.BUZZWORD_SPECIFIC_CORPUS)
    # migrate handling
    except TypeError as error:
        print(f"Problem: {str(error)}")
        return html.Div("")

    freq_space, table = _freq_space(corpus)
    chart_space = _chart_space(table)
    conc_space = _concordance_space(corpus)

    text_style = {"maxWidth": "800px", "margin": "auto", "marginBottom": "40px"}
    sty = {"maxWidth": "40vw", "minWidth": "40vw", "marginLeft": "100px"}
    freq_text = dcc.Markdown(text["freq"], style={}, className="col-sm")

    freq_and_text = html.Div(
        className="container",
        children=html.Div(
            className="row",
            style={"height": "70vh", "marginBottom": "10px", "marginTop": "50px"},
            children=[freq_space, freq_text],
        ),
    )

    text_style = {"maxWidth": "800px", "margin": "auto", "marginBottom": "40px"}
    sty = {"maxWidth": "40vw", "minWidth": "40vw", "marginLeft": "100px"}
    chart_text = dcc.Markdown(text["vis"], style={"marginTop": "100px"}, className="col-sm")

    chart_and_text = html.Div(
        className="container",
        children=html.Div(className="row", children=[chart_text, chart_space]),
        style={"marginBottom": "50px"},
    )

    children = [
        dcc.Markdown(text["intro"], style={**text_style, **{"marginTop": "140px"}}),
        html.Img(
            src="/static/swiss-law/search-1.png",
            style={"width": "70%", "marginTop": "-30px", "marginBottom": "30px"},
            className="center",
        ),
        dcc.Markdown(text["intro2"], style={**text_style, **{"marginBottom": "40px"}}),
        html.Img(
            src="/static/swiss-law/search-2.png",
            style={"width": "70%", "marginTop": "-30px", "marginBottom": "30px"},
            className="center",
        ),
        freq_and_text,
        # dcc.Markdown(text["calc"], style=text_style),
        chart_and_text,
        dcc.Markdown(text["conc"], style=text_style),
        conc_space,
        dcc.Markdown(text["end"], style=text_style),
    ]
    layout = dcc.Loading(html.Div(children), fullscreen=True)
    return layout


def _chart_space(table):
    from explorer.tabs import _build_chart_space

    iterate_over = [(1, "stacked_bar")]
    return _build_chart_space(table, iterate_over, width="60vw", no_from_select=True)


def _freq_space(corpus):

    style_index = style.FILE_INDEX
    table, columns, data = _quick_freq(corpus, None)
    style_index["if"]["column_id"] = table.index.name

    freq_table = dcc.Loading(
        type="default",
        children=[
            dash_table.DataTable(
                id="example-freq",
                columns=columns,
                data=data,
                editable=False,
                # style_cell={
                #    **style.HORIZONTAL_PAD_5,
                #    **{"maxWidth": "145px", "minWidth": "60px"},
                # },
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                row_deletable=False,
                selected_rows=[],
                page_current=0,
                page_size=10,
                page_action="native",
                fixed_rows={"headers": True, "data": 0},
                # virtualization=True,
                # style_table={"width": "40vw"},
                style_header=style.BOLD_DARK,
                style_cell_conditional=style.LEFT_ALIGN,
                style_data_conditional=[style_index] + style.STRIPES,
                merge_duplicate_headers=True,
                # export_format="xlsx",
                # export_headers="display",
                css=[{"selector": ".show-hide", "rule": "display: none"}],
            )
        ],
    )

    styled = {"maxWidth": "50vw", "minWidth": "50vw", "height": "35vh", "marginBottom": "70px"}
    freq_space = html.Div([freq_table], style=styled, className="col-sm")
    return freq_space, table


def _concordance_space(corpus):
    query_space = dcc.Input(
        id="conc-query-string",
        type="text",
        placeholder="Enter search query...",
        size="90vw",
        style={**style.MARGIN_5_MONO, **{"marginRight": "10px"}},
        className="input-lg form-control",
    )
    search = html.Button(
        "Search", id="do-conc", style=style.MARGIN_5_MONO, className="form-control"
    )
    tstyle = dict(width="100%", marginBottom="10px", **style.CELL_MIDDLE_35)
    toolbar = html.Div(
        [html.Div(i, style=tstyle) for i in (query_space, search)], style={"marginBottom": "5px"}
    )
    style_data = [style.STRIPES[0], style.INDEX[0]] + style.CONC_LMR
    columns, data = _quick_concordance(corpus, "ordnung")
    rule = "display: inline; white-space: inherit; " + "overflow: inherit; text-overflow: inherit;"
    conc_table = html.Div(
        dcc.Loading(
            type="default",
            children=[
                dash_table.DataTable(
                    id="example-conc",
                    css=[
                        {"selector": ".dash-cell div.dash-cell-value", "rule": rule},
                        {"selector": ".show-hide", "rule": "display: none"},
                    ],
                    columns=columns,
                    data=data,
                    editable=False,
                    style_cell={**style.HORIZONTAL_PAD_5, **{"minWidth": "60px"}},
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    row_deletable=True,
                    selected_rows=[],
                    page_action="none",
                    fixed_rows={"headers": True, "data": 0},
                    page_current=0,
                    page_size=10,
                    # virtualization=True,
                    # style_table={'width': '50vw'},
                    style_as_list_view=True,
                    style_header=style.BOLD_DARK,
                    style_cell_conditional=style.LEFT_ALIGN_CONC,
                    style_data_conditional=style_data,
                    merge_duplicate_headers=True,
                    # export_format="xlsx",
                    # export_headers="display",
                )
            ],
        )
    )
    windowed = {
        "maxWidth": "80vw",
        "marginLeft": "50px",
        "marginRight": "50px",
        "marginBottom": "70px",
    }
    conc_space = html.Div([toolbar, conc_table], style=windowed)
    return conc_space


def _quick_freq(corpus, query):
    df = corpus.just.wordclass.NOUN.just.word("[A-Za-z]{3,}", regex=True)
    df = df.table(subcorpora="year", show="l", relative=True).round(2).iloc[:, :50].T
    df.index.names = ["lemma"]

    this_df = df.reset_index()

    columns = [
        {"name": i, "id": i, "deletable": False, "hideable": True, "presentation": False}
        for i in this_df.columns
    ]
    data = this_df.to_dict("rows")
    return df, columns, data


def _quick_concordance(corpus, query):
    df = corpus.just.word(query, exact_match=True, case=False)
    df = df.conc(n=999, window=(80, 80), metadata=["year", "file", "s"])
    df["file"] = df["file"].apply(os.path.basename)
    just = ["left", "match", "right", "year", "file", "s"]
    if "speaker" in df.columns:
        just.append("speaker")
    df = df[just]
    columns = [
        {
            "name": _capitalize_first(SHORT_TO_COL_NAME.get(i, i)),
            "id": i,
            "deletable": i not in ["left", "match", "right"],
            "hideable": True,
            "presentation": ("markdown" if i == "match" else None),
        }
        for i in df.columns
    ]
    data = df.to_dict("rows")
    return columns, data


app = DjangoDash(settings.BUZZWORD_SPECIFIC_CORPUS, suppress_callback_exceptions=True)
app.layout = _make_layout()


@app.expanded_callback(
    [Output("example-conc", "columns"), Output("example-conc", "data")],
    [Input("do-conc", "n_clicks")],
    [State("conc-query-string", "value")],
)
def _simple_concordance(do_conc, query, **kwargs):
    if not do_conc:
        return no_update
    try:
        corpus = _get_corpus(settings.BUZZWORD_SPECIFIC_CORPUS)
    # migrate handling
    except TypeError:
        return [], []
    columns, data = _quick_concordance(corpus, query.strip())
    return columns, data


@app.expanded_callback(
    Output("chart-1", "figure"),
    [Input("figure-button-1", "n_clicks")],
    [
        State("chart-type-1", "value"),
        State("chart-top-n-1", "value"),
        State("chart-transpose-1", "on"),
    ],
)
def _new_chart(
    n_clicks, chart_type, top_n, transpose, **kwargs,
):
    """
    Make new chart by kind. Do it 5 times, once for each chart space
    """
    # before anything is loaded, do nothing
    if n_clicks is None:
        return no_update

    try:
        corpus = _get_corpus(settings.BUZZWORD_SPECIFIC_CORPUS)
    # migrate handling
    except TypeError:
        return [], []

    df, _, _ = _quick_freq(corpus, None)

    # transpose and cut down items to plot
    if transpose:
        df = df.T
    df = df.iloc[:, :top_n]

    # generate chart
    return _df_to_figure(df, chart_type)
