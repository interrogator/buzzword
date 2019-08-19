import base64
import os
import traceback
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
from buzz.constants import SPACY_LANGUAGES
from buzz.corpus import Corpus
from buzzword.parts.main import app, CORPORA, INITIAL_TABLES, CORPUS_META, CONFIG
from buzzword.parts.strings import _slug_from_name, _make_description
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from buzzword.parts.nav import navbar
from buzzword.parts import style


def _make_row(row_data, index=None, upload=False):
    """
    Make row for corpus table
    """
    clas = "flash" if upload else "normal-row"
    row = [html.Td(children=index, className=clas)]
    for key, value in row_data.items():
        if key == "link":
            continue
        if key == "id":
            cell = html.Td(html.A(href=row_data["link"], children=value, className=clas))
        elif key == "title":
            a = html.A(href=row_data["link"], children=value, className=clas)
            cell = html.Td(a, className=clas)
        elif key == "url":
            if value:
                hyper = html.A(href=value, children="ⓘ", target="_blank", className=clas)
                cell = html.Td(children=hyper, className=clas)
            else:
                cell = html.Td(children="", className=clas)
        else:
            cell = html.Td(children=value, className=clas)
        row.append(cell)
    return html.Tr(row)


def _make_corpus_table():
    """
    Create HTML table with links to each corpus in corpora.json
    """
    import locale

    locale.setlocale(locale.LC_ALL, "")
    fields = ["#", "title", "date", "language", "description", "info", "tokens"]
    columns = [html.Tr([html.Th(col) for col in fields])]
    rows = list()
    is_empty = True
    for i, (corpus, metadata) in enumerate(CORPUS_META.items(), start=1):
        if metadata.get("disabled"):
            continue
        slug = metadata["slug"]
        link = "explore/{}".format(slug)
        adate = metadata.get("date", "undated")
        lang = metadata.get("language", "unknown").capitalize()
        tokens = "{:n}".format(metadata["len"])
        url = metadata.get("url", "none")
        desc = metadata["desc"]
        tups = [
            ("title", corpus),
            ("date", adate),
            ("language", lang),
            ("description", desc),
            ("url", url),
            ("tokens", tokens),
            ("link", link),
        ]
        rows.append(_make_row(OrderedDict(tups), i))
        is_empty = False
    style = {"width": "1000px"}
    data = columns + rows
    table = html.Table(id="corpus-table", children=data, style=style)
    return table, is_empty


def _make_upload_parse_space():
    """
    Make space for uploading files, and toolbar for submit
    """
    upload = dcc.Upload(
        id="upload-data",
        children=html.Div(["Drag-and-drop or ", html.A("select files")]),
        style={
            "width": "1000px",
            "height": "100px",
            "lineHeight": "100px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "marginBottom": "10px",
        },
        # Allow multiple files to be uploaded
        multiple=True,
    )
    corpus_name = dcc.Input(
        id="upload-corpus-name",
        type="text",
        placeholder="Enter a name for your corpus",
        style={**style.BLOCK, **{"width": "550px", "fontFamily": "monospace"}},
    )
    lang = dcc.Dropdown(
        placeholder="Language of corpus",
        id="corpus-language",
        options=[{"value": v, "label": k} for k, v in SPACY_LANGUAGES.items()],
        style={**style.BLOCK, **{"width": "230px", "marginRight": "5px", "fontFamily": "monospace"}},
    )
    upload = html.Div(children=[upload, html.Div(id="show-upload-files")])
    dialog = dcc.ConfirmDialog(id="dialog-upload", message="")
    upload_button = html.Button(
        "Upload and parse",
        id="upload-parse-button",
        style={**style.BLOCK, **{"width": "205px", "marginLeft": "5px", "fontFamily": "monospace"}},
    )
    bits = [corpus_name, lang, upload_button]
    sty = {"width": "1000px", **style.VERTICAL_MARGINS, "marginBottom": "20px"}
    toolbar = html.Div(bits, style=sty)
    return html.Div(
        id="upload-space",
        children=dcc.Loading(type="default", children=[dialog, upload, toolbar]),
    )


def _store_corpus(contents, filenames, slug):
    """
    From content and filenames, build a corpus and return the path to it
    """
    corpus_size = 0
    is_parsed = all(i.endswith(("conll", "conllu")) for i in filenames)
    if is_parsed:
        slug = slug + "-parsed"
    store_at = os.path.join(CONFIG["root"], "uploads", slug)
    os.makedirs(store_at)
    for content, filename in zip(contents, filenames):
        content_type, content_string = content.split(",", 1)
        decoded = base64.b64decode(content_string)
        corpus_size += len(decoded)
        outpath = os.path.join(store_at, filename)
        with open(outpath, "wb") as fo:
            fo.write(decoded)
    return store_at, is_parsed, corpus_size


def _validate_input(contents, names, corpus_name, slug):
    """
    Check that uploaded corpus-to-be is valid
    """
    endings = set([os.path.splitext(i)[-1] for i in names])
    if not endings:
        return "File extension not provided."
    if len(endings) > 1:
        return "All uploaded files need to have the same extension."
    allowed = {".conll", ".conllu", ".txt"}
    if endings.pop() not in allowed:
        allowed = ", ".join(allowed)
        return "Uploaded file extension must be one of: {}".format(allowed)
    up_dir_exists = os.path.isdir(os.path.join(CONFIG["root"], "uploads", slug))
    if corpus_name in CORPUS_META or up_dir_exists:
        return f"A corpus named '{corpus_name}' already exists. Try a different name."
    return ""


@app.callback(
    [
        Output("dialog-upload", "displayed"),
        Output("dialog-upload", "message"),
        Output("corpus-table", "children"),
    ],
    [Input("upload-parse-button", "n_clicks")],
    [
        State("upload-data", "contents"),
        State("upload-data", "filename"),
        State("corpus-language", "value"),
        State("upload-corpus-name", "value"),
        State("corpus-table", "children"),
    ],
)
def _upload_files(n_clicks, contents, names, corpus_lang, corpus_name, table_rows):
    """
    Callback when the user clicks 'upload and parse'
    """
    from datetime import date

    if n_clicks is None:
        raise PreventUpdate

    slug = _slug_from_name(corpus_name)
    msg = _validate_input(contents, names, corpus_name, slug)

    if msg:
        return bool(msg), msg, table_rows

    path, is_parsed, size = _store_corpus(contents, names, slug)
    corpus = Corpus(path)
    if not is_parsed:
        try:
            corpus = corpus.parse(cons_parser=None, language=corpus_lang)
        except Exception as error:
            msg = f"Problem when parsing the corpus: {str(error)}"
            traceback.print_exc()
            return bool(msg), msg, table_rows

    CORPORA[slug] = corpus.load()
    CORPUS_META[corpus_name] = dict(slug=slug)
    INITIAL_TABLES[slug] = CORPORA[slug].table(show="p", subcorpora="file")
    slug = _slug_from_name(corpus_name)
    href = "/explore/{}".format(slug)
    index = len(CORPUS_META)
    adate = date.today().strftime("%d.%m.%Y")
    desc = _make_description(names, size)
    toks = "{:n}".format(len(CORPORA[slug]))
    # get long name for language
    long_lang = next(k for k, v in SPACY_LANGUAGES.items() if v == corpus_lang)
    long_lang = long_lang.capitalize()
    tups = [
        ("title", corpus_name),
        ("date", adate),
        ("language", long_lang),
        ("description", desc),
        ("url", None),
        ("tokens", toks),
        ("link", href),
    ]
    table_rows.append(_make_row(OrderedDict(tups), index, upload=True))
    return bool(msg), msg, table_rows


@app.callback(
    Output("show-upload-files", "children"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")],
)
def show_uploaded(contents, filenames):
    """
    Display files for upload underneath the upload space
    """
    if not contents:
        raise PreventUpdate
    markdown = "* " + "\n* ".join([i for i in filenames[:10]])
    if len(filenames) > 10:
        rest = len(filenames) - 10
        markdown += f"\n* and {rest} more ..."
    return dcc.Markdown(markdown)


header = html.H2("buzzword: a tool for analysing annotated linguistic data")

# if no corpora available, do not show this table
table, is_empty = _make_corpus_table()
avail = ""
if not is_empty:
    head = html.H3("Available corpora", style=style.VERTICAL_MARGINS)
    text = "Select your corpus from the list below."
    text = html.P(text, style=style.VERTICAL_MARGINS)
    demos = html.Div([head, text, table])
    avail = "Otherwise, you can try out the corpora below."

intro = html.P(
    "Here you can create and explore parsed and annotated corpora. "
    "If you want to work with your own corpus, simply upload plain text files, "
    "annotated text files, or CONLL-U files." + avail
)
uphead = html.H3("Upload data", style=style.VERTICAL_MARGINS)

link = "https://buzzword.readthedocs.io/en/latest/building/'"
md = (
    "You can upload either CONLL-U files, or plaintext with optional annotations. "
    "See [`Creating corpora`]({}) for more information.".format(link)
)
upload_text = dcc.Markdown(md)

upload = _make_upload_parse_space()

content = [header, intro, uphead, upload_text, upload]
if not is_empty:
    content.append(demos)
content_style = {"display": "inline-block", "width": "1000px", "textAlign": "left"}
content = html.Div(content, style=content_style)
content = html.Div(content, style={"textAlign": "center"})
components = [navbar, content]
layout = html.Div(components)
