# flake8: noqa


import json
import os

import dash
from dash import no_update
import dash_core_components as dcc
import dash_html_components as html

from django_plotly_dash import DjangoDash

import dash_table

from django.conf import settings

from buzz.constants import SHORT_TO_COL_NAME
from explore.models import Corpus
from explorer.strings import _capitalize_first
from explorer.helpers import _get_corpus
from explorer.chart import _df_to_figure
from explorer import style


WORDCLASSES = {
    "ADJ",
    "ADP",
    "ADV",
    "AUX",
    "CCONJ",
    "DET",
    "INTJ",
    "NOUN",
    "NUM",
    "PART",
    "PRON",
    "PROPN",
    "PUNCT",
    "SCONJ",
    "VERB",
    "X",
}


def _make_layout(slug):
    path = f"static/{slug}/example.json"
    with open(path) as fo:
        text = json.load(fo)

    try:
        corpus = _get_corpus(slug)
    # migrate handling
    except TypeError as error:
        print(f"Problem: {str(error)}")
        return html.Div("")

    freq_space, table = _freq_space(corpus)
    chart_space = _chart_space(table)
    conc_space = _concordance_space(corpus, slug)

    freq_text = dcc.Markdown(text["freq"], style={}, className="row")
    freq_img = html.Img(src="/static/swiss-law/freq-toolbar.png", width="110%", className="row",)
    freq_text2 = dcc.Markdown(text["freq2"], style={}, className="row")
    freq_text = html.Div(
        [freq_text, freq_img, freq_text2],
        style={"marginLeft": "30px"},
        className="container col-7 col-md-7 col-lg-7 col-xl-7 col-xxl-7",
    )

    freq_and_text = html.Div(
        className="container",
        children=html.Div(
            className="row",
            style={"marginBottom": "10px", "marginTop": "50px"},
            children=[freq_space, freq_text],
        ),
    )

    text_style = {"maxWidth": "1000px", "margin": "auto", "marginBottom": "40px"}
    sty = {"maxWidth": "40vw", "minWidth": "40vw", "marginLeft": "100px"}
    chart_text = dcc.Markdown(
        text["vis"],
        style={"marginTop": "50px"},
        className="col-7 col-md-7 col-lg-4 col-xl-4 col-xxl-4",
    )

    chart_and_text = html.Div(
        className="container",
        children=html.Div(className="row", children=[chart_text, chart_space]),
        style={"marginBottom": "50px"},
    )

    children = [
        dcc.Markdown(
            "# **Swiss Digital Law Discovery** (*Sdilaw*):",
            style={**text_style, **{"marginTop": "140px", "marginBottom": "20px"}},
        ),
        dcc.Markdown(text["intro"], style=text_style),
        html.Img(
            src="/static/swiss-law/search-1.png",
            style={
                "width": "70%",
                "marginTop": "-30px",
                "marginBottom": "30px",
                "maxWidth": "1000px",
            },
            className="center",
        ),
        dcc.Markdown(text["intro2"], style={**text_style, **{"marginBottom": "40px"}}),
        html.Img(
            src="/static/swiss-law/search-2.png",
            style={
                "width": "70%",
                "marginTop": "-30px",
                "marginBottom": "30px",
                "maxWidth": "1000px",
            },
            className="center",
        ),
        freq_and_text,
        # dcc.Markdown(text["calc"], style=text_style),
        chart_and_text,
        dcc.Markdown(text["conc"], style=text_style),
        conc_space,
        dcc.Markdown(text["end"], style=text_style),
    ]
    layout = html.Div(children, className="col-12 col-md-12 col-lg-12 col-xl-12 col-xxl-12")
    layout = html.Div(layout, className="row")
    layout = html.Div(layout, className="container")
    return dcc.Loading(layout, fullscreen=False, id="example-loading")
    # return layout


def _chart_space(table):
    from explorer.tabs import _build_chart_space

    iterate_over = [(1, "stacked_bar")]
    space = _build_chart_space(
        table, iterate_over, width="100%", height="400px", no_from_select=True
    )
    return html.Div(space, className="col-6 col-md-6 col-lg-8 col-xl-8 col-xxl-8")


def _freq_space(corpus, wordclass="NOUN"):

    wordclass = wordclass.upper() if wordclass.upper() in WORDCLASSES else "NOUN"

    style_index = style.FILE_INDEX

    select_wordclass = dcc.Dropdown(
        placeholder="Features to show",
        multi=False,
        id="example-wordclass-dropdown",
        options=[dict(value=k, label=k) for k in sorted(WORDCLASSES)],
        value="NOUN",
        className="pull-right",
        style={
            **style.MARGIN_5_MONO,
            **{"marginLeft": "0px", "width": "100%", "marginBottom": "5px"},
        },
    )

    table, columns, data = _quick_freq(corpus, wordclass=wordclass)
    style_index["if"]["column_id"] = table.index.name

    freq_table = dash_table.DataTable(
        id="example-freq",
        columns=columns,
        data=data,
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_deletable=False,
        selected_rows=[],
        page_current=0,
        page_size=10,
        page_action="native",
        fixed_rows={"headers": True, "data": 0},
        style_header=style.BOLD_DARK,
        style_table={"overflowX": "scroll"},
        style_data_conditional=style.STRIPES,
        merge_duplicate_headers=True,
        # export_format="xlsx",
        # export_headers="display",
        css=[{"selector": ".show-hide", "rule": "display: none"}],
    )

    column = "col-4 col-md-4 col-lg-4 col-xl-4 col-xxl-4 float-left"
    freq_space = html.Div([select_wordclass, freq_table], style={}, className=column)
    return freq_space, table


def _concordance_space(corpus, slug):
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
    query = Corpus.objects.get(slug=slug).example_concordance
    columns, data = _quick_concordance(corpus, query)
    rule = "display: inline; white-space: inherit; " + "overflow: inherit; text-overflow: inherit;"
    conc_table = dash_table.DataTable(
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
            page_action="native",
            fixed_rows={"headers": True, "data": 0},
            page_current=0,
            page_size=50,
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

    windowed = {
        "maxWidth": "80vw",
        "marginLeft": "50px",
        "marginRight": "50px",
        "marginBottom": "70px",
    }
    conc_space = html.Div([toolbar, conc_table], style=windowed)
    return conc_space


def _quick_freq(corpus, wordclass="NOUN"):
    # todo: pass in initial query...
    df = getattr(corpus.just.wordclass, wordclass).just.word("[A-Za-z]{3,}", regex=True)
    if "year" in corpus.columns:
        subcorpora = "year"
        #corpus["year"] = corpus["year"].astype(str)
    elif "speaker" in corpus.columns:
        subcorpora = "speaker"
        #corpus["speaker"] = corpus["speaker"].astype(str)
    else:
        subcorpora = "file"
    df = df.table(subcorpora=subcorpora, show="l", relative=True).round(2).iloc[:, :50].T
    df.index.names = ["lemma"]

    # df.index = df.index.astype(object)
    df.columns = df.columns.astype(object)

    num_cols = len(df.columns)
    index_width = "55%" if len(df.columns) == 3 else "100px"
    item_width = "15%" if len(df.columns) == 3 else "30%"

    this_df = df.reset_index()

    columns = [
        {
            "name": x,
            "id": x,
            "deletable": False,
            "hideable": True,
            "presentation": False,
            "width": item_width if i else index_width 
        } 
        for i, x in enumerate(this_df.columns)
    ]
    data = this_df.to_dict("rows")
    return df, columns, data

def _quick_concordance(corpus, query):
    df = corpus.just.word(query, exact_match=True, case=False)
    just = ["left", "match", "right", "file", "s"]
    meta = ["file", "s"]
    for field in ["speaker", "year"]:
        if field in df.columns:
            just.append(field)
            meta.append(field)

    df = df.conc(n=999, window=(80, 80), metadata=meta)
    df["file"] = df["file"].apply(os.path.basename)

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


def make_app(slug):
    app = DjangoDash("example", suppress_callback_exceptions=True)
    app.layout = _make_layout(slug)
    from . import callbacks
    return app
