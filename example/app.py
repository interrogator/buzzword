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
from explorer import style
css = "https://codepen.io/chriddyp/pen/bWLwgP.css"


def _make_layout():
    with open("static/swiss-law/example.json") as fo:
        text = json.load(fo)
    conc_space = concordance_space()
    text_style = {"maxWidth": "800px", "margin": "auto", "marginBottom": "40px"}
    children = [dcc.Markdown(text["intro"], style={**text_style, **{"marginTop": "140px"}}),
                dcc.Markdown(text["freq"], style=text_style),
                dcc.Markdown(text["calc"], style=text_style),
                dcc.Markdown(text["vis"], style=text_style),
                dcc.Markdown(text["conc"], style=text_style),
                conc_space,
                dcc.Markdown(text["end"], style=text_style)]
    layout = html.Div(children)
    return layout


def concordance_space():
    query_space = dcc.Input(
            id="conc-query-string",
            type="text",
            placeholder="Enter search query...",
            size="60",
            style=style.MARGIN_5_MONO,
    )
    search = html.Button("Search", id="do-conc", style=style.MARGIN_5_MONO)
    tstyle = dict(width="100%", marginBottom="10px", **style.CELL_MIDDLE_35)
    toolbar = html.Div([html.Div(i, style=tstyle) for i in (query_space, search)])
    style_data = [style.STRIPES[0], style.INDEX[0]] + style.CONC_LMR
    columns, data = _quick_concordance("gegen")
    rule = (
        "display: inline; white-space: inherit; "
        + "overflow: inherit; text-overflow: inherit;"
    )
    conc_table = html.Div(
        dcc.Loading(
            type="default",
            children=[
                dash_table.DataTable(
                    id="example-conc",
                    css=[{"selector": ".dash-cell div.dash-cell-value", "rule": rule}, {"selector": ".show-hide", "rule": "display: none"}],
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
                    #page_size=settings.PAGE_SIZE,
                    virtualization=True,
                    #style_table={'height': '1000px'},
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
        #style={"display": "table"}
    )
    windowed = {**style.VERTICAL_MARGINS, **{"width": "70vw", "height": "35vh", "margin": "auto"}}
    conc_space = html.Div([toolbar, conc_table], style=windowed)
    return conc_space

def _get_year(cell):
    return cell[:4]

def _quick_concordance(query):
    corpus = _get_corpus(settings.BUZZWORD_SPECIFIC_CORPUS)
    df = corpus.just.word(query, exact_match=True)
    df = df.conc(n=999)
    df["file"] = df["file"].apply(os.path.basename)
    df["year"] = df["file"].apply(_get_year)
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
            "presentation": ("markdown" if i == "match" else None)
        }
        for i in df.columns
    ]
    data = df.to_dict("rows")
    return columns, data


app = DjangoDash("swisslaw", external_stylesheets=[css], suppress_callback_exceptions=True)
app.layout = _make_layout()


@app.callback(
    [Output("example-conc", "columns"),
    Output("example-conc", "data")],
    [Input("do-conc", "n_clicks")],
    [State("conc-query-string", "value")]
)
def _simple_concordance(do_conc, query):
    if not do_conc:
        return no_update
    columns, data = _quick_concordance(query)
    return columns, data

