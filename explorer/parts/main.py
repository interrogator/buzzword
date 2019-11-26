"""
buzzword: run on startup, corpus loading and app initialisation
"""

import json
import os

from buzz.corpus import Corpus
from django_plotly_dash import DjangoDash

from ..parts.configure import _configure_buzzword
from ..parts.helpers import _preprocess_corpus
from ..parts.strings import _slug_from_name

external_stylesheets = []

app = DjangoDash("buzzword", external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

GLOBAL_CONFIG = _configure_buzzword("buzzword")

ROOT = GLOBAL_CONFIG["root"]


def _get_corpus_config(local_conf, global_conf, name):
    """
    Return global conf plus individual settings for corpus
    """
    conf = {**global_conf}
    settings = {"max_dataset_rows", "drop_columns", "add_governor", "load", "slug"}
    for setting in settings:
        loc = local_conf.get(setting)
        if loc is not None:
            conf[setting] = loc
        else:
            if setting == "slug":
                conf[setting] = _slug_from_name(name)
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
        slug = metadata.get("slug", _slug_from_name(corpus_name))
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
