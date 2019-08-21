"""
buzzword: run on startup, corpus loading and app initialisation
"""

import dash
from buzz.corpus import Corpus
import json
import os
from buzzword.parts.helpers import _preprocess_corpus
from buzzword.parts.configure import _configure_buzzword

external_stylesheets = [
    "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css",
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
app.title = "buzzword"
server = app.server

GLOBAL_CONFIG = _configure_buzzword(__name__)

ROOT = GLOBAL_CONFIG["root"]


def _get_corpus_config(local_conf, global_conf, name):
    """
    Return global conf plus individual settings for corpus
    """
    conf = {**global_conf}
    settings = {"max_dataset_rows", "drop_columns", "add_governor", "load"}
    for setting in settings:
        loc = local_conf.get(setting)
        if loc is not None:
            conf[setting] = loc
    conf["corpus_name"] = name
    return conf


def _get_corpora(corpus_meta):
    """
    Load in all available corpora and make their initial tables

    This is run when the app starts up
    """
    corpora = dict()
    tables = dict()
    corpora_config = dict()
    for i, (corpus_name, metadata) in enumerate(corpus_meta.items(), start=1):
        if metadata.get("disabled"):
            print("Skipping corpus because it is disabled: {}".format(corpus_name))
            continue
        slug = metadata["slug"]
        corpus = Corpus(metadata["path"])
        conf = _get_corpus_config(metadata, GLOBAL_CONFIG, corpus_name)
        if conf["load"]:
            print("Loading corpus into memory: {} ...".format(corpus_name))
            corpus = corpus.load(add_governor=conf["add_governor"])
            corpus = _preprocess_corpus(corpus, **conf)
        else:
            print("NOT loading corpus into memory: {} ...".format(corpus_name))
        initial_table = corpus.table(show="p", subcorpora="file")
        corpora[slug] = corpus
        tables[slug] = initial_table
        corpora_config[slug] = conf
    return corpora, tables, corpora_config


def _get_corpora_meta(corpora_file):
    """
    Get the contents of corpora.json, or an empty dict
    """
    exists = os.path.isfile(corpora_file)
    if not exists:
        print("Corpora file not found at {}!".format(corpora_file))
        return dict()
    with open(corpora_file, "r") as fo:
        return json.loads(fo.read())


CORPUS_META = _get_corpora_meta(GLOBAL_CONFIG.get("corpora_file"))

CORPORA, INITIAL_TABLES, CORPORA_CONFIGS = _get_corpora(CORPUS_META)
