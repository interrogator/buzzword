"""
buzzword: main page and its callbacks; loading corpus table
"""

import base64
import os
import traceback
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
from buzz.constants import SPACY_LANGUAGES
from buzz.corpus import Corpus
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..parts import style
from ..parts.main import (CORPORA, CORPORA_CONFIGS, CORPUS_META, GLOBAL_CONFIG,
                          INITIAL_TABLES, ROOT, app)
from ..parts.strings import _make_description, _slug_from_name


def _store_corpus(contents, filenames, slug):
    """
    From content and filenames, build a corpus and return the path to it
    """
    corpus_size = 0
    is_parsed = all(i.endswith(("conll", "conllu")) for i in filenames)
    if is_parsed:
        slug = slug + "-parsed"
    store_at = os.path.join(ROOT, "uploads", slug)
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
    up_dir_exists = os.path.isdir(os.path.join(ROOT, "uploads", slug))
    if corpus_name in CORPUS_META or up_dir_exists:
        return f"A corpus named '{corpus_name}' already exists. Try a different name."
    return ""


@app.callback(
    [
        Output("dialog-upload", "displayed"),
        Output("dialog-upload", "message"),
        Output("corpus-table", "children"),
        Output("session-configs", "data"),
    ],
    [Input("upload-parse-button", "n_clicks")],
    [
        State("upload-data", "contents"),
        State("upload-data", "filename"),
        State("corpus-language", "value"),
        State("upload-corpus-name", "value"),
        State("corpus-table", "children"),
        State("session-configs", "data"),
    ],
)
def _upload_files(n_clicks, contents, names, corpus_lang, corpus_name, table_rows, session_configs):
    """
    Callback when the user clicks 'upload and parse'
    """
    from datetime import date

    if n_clicks is None:
        raise PreventUpdate

    slug = _slug_from_name(corpus_name)
    msg = _validate_input(contents, names, corpus_name, slug)

    if msg:
        return bool(msg), msg, table_rows, session_configs

    path, is_parsed, size = _store_corpus(contents, names, slug)
    corpus = Corpus(path)
    if not is_parsed:
        try:
            corpus = corpus.parse(cons_parser=None, language=corpus_lang)
        except Exception as error:
            msg = f"Problem when parsing the corpus: {str(error)}"
            traceback.print_exc()
            return bool(msg), msg, table_rows, session_configs

    corpus = corpus.load()

    CORPORA[slug] = corpus
    conf = dict(
        **GLOBAL_CONFIG,
        slug=slug,
        len=len(corpus),
        corpus_name=corpus_name,
    )
    CORPUS_META[corpus_name] = conf
    CORPORA_CONFIGS[slug] = conf
    INITIAL_TABLES[slug] = CORPORA[slug].table(show="p", subcorpora="file")

    href = "/explore/{}".format(slug)
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
    # put it at start of table :)
    row = _make_row(OrderedDict(tups), 0, upload=True)
    table_rows = [table_rows[0], row] + table_rows[1:]
    session_configs[slug] = conf
    return bool(msg), msg, table_rows, session_configs


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
    avail = " Otherwise, you can try out the corpora below."

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
navbar = _make_navbar(GLOBAL_CONFIG["debug"])
components = [navbar, content]
layout = html.Div(components)
