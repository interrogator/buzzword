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

CONFIG = _configure_buzzword(__name__)


def _get_corpus_config(local_conf, global_conf):
    """
    Return global conf plus individual settings for corpus
    """
    conf = {**global_conf}
    settings = {"max_dataset_rows", "drop_columns", "add_governor", "load"}
    for setting in settings:
        loc = local_conf.get(setting)
        if loc is not None:
            conf[setting] = loc
    return conf


def _get_corpora(corpus_meta):
    """
    Load in all available corpora and make their initial tables

    This is run when the app starts up
    """
    corpora = dict()
    tables = dict()
    for i, (corpus_name, metadata) in enumerate(corpus_meta.items(), start=1):
        if metadata.get("disabled"):
            print("Skipping corpus because it is disabled: {}".format(corpus_name))
            continue
        corpus = Corpus(metadata["path"])
        conf = _get_corpus_config(metadata, CONFIG)
        if conf["load"]:
            print("Loading corpus into memory: {} ...".format(corpus_name))
            corpus = corpus.load(add_governor=conf["add_governor"])
            corpus = _preprocess_corpus(corpus, **conf)
        else:
            print("NOT loading corpus into memory: {} ...".format(corpus_name))
        initial_table = corpus.table(show="p", subcorpora="file")
        corpora[metadata["slug"]] = corpus
        tables[metadata["slug"]] = initial_table
    return corpora, tables


def _get_corpora_meta(config):
    """
    Get the contents of corpora.json, or an empty dict
    """
    corpora_file = config.get("corpora_file")
    exists = os.path.isfile(corpora_file)
    if not exists:
        print("Corpora file not found at {}!".format(corpora_file))
        return dict()
    with open(corpora_file, "r") as fo:
        return json.loads(fo.read())


CORPUS_META = _get_corpora_meta(CONFIG)

CORPORA, INITIAL_TABLES = _get_corpora(CORPUS_META)
