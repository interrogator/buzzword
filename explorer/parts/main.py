"""
buzzword explorer: run on startup, corpus loading and app initialisation
"""


from buzz.corpus import Corpus
from django_plotly_dash import DjangoDash

from .configure import configure_buzzword
from .helpers import (_get_corpora_meta, _get_corpus, _get_initial_table,
                      _preprocess_corpus, register_callbacks)
from .strings import _slug_from_name
from .tabs import make_explore_page

app = DjangoDash("buzzword", suppress_callback_exceptions=True)

GLOBAL_CONFIG = configure_buzzword()

ROOT = GLOBAL_CONFIG["root"]

LAYOUTS = dict()


def _get_corpus_config(corpus, global_conf):
    """
    Return global conf plus individual settings for corpus
    """
    conf = {**global_conf}
    settings = {"max_dataset_rows", "drop_columns", "add_governor", "load", "slug"}
    for setting in settings:
        loc = getattr(corpus, setting, None)
        if loc is not None:
            conf[setting] = loc
    conf["corpus_name"] = corpus.name
    return conf


def _get_corpora(corpus_meta):
    """
    Load in all available corpora and make their initial tables

    This is run when the app starts up
    """
    corpora = dict()
    tables = dict()
    corpora_config = dict()
    for corpus in corpus_meta:
        if corpus.disabled:
            print("Skipping corpus because it is disabled: {}".format(corpus.name))
            continue
        buzz_corpus = Corpus(corpus.path)
        conf = _get_corpus_config(corpus, GLOBAL_CONFIG)
        if conf["load"]:
            print("Loading corpus into memory: {} ...".format(corpus.name))
            buzz_corpus = buzz_corpus.load(add_governor=conf["add_governor"])
            buzz_corpus = _preprocess_corpus(buzz_corpus, **conf)
        else:
            print("NOT loading corpus into memory: {} ...".format(corpus.name))
        initial_table = buzz_corpus.table(show="p", subcorpora="file")
        corpora[corpus.slug] = buzz_corpus
        tables[corpus.slug] = initial_table
        corpora_config[corpus.slug] = conf
    return corpora, tables, corpora_config


def load_layout(slug, set_and_register=True):
    """
    Django can import this function to set the correct dataset on explore page

    Return app instance, just in case django has a use for it.
    """
    conf = CORPORA_CONFIGS[slug]
    # store the default explore for each corpus in a dict for speed
    if slug in LAYOUTS:
        layout = LAYOUTS[slug]
    else:
        corpus = _get_corpus(slug)
        table = _get_initial_table(slug)
        conf["len"] = conf.get("len", len(corpus))
        layout = make_explore_page(corpus, table, conf, CORPORA_CONFIGS)
        LAYOUTS[slug] = layout
    if set_and_register:
        app.layout = layout
        register_callbacks()
    return app


def load_corpora():
    global CORPUS_META, CORPORA, INITIAL_TABLES, CORPORA_CONFIGS

    CORPUS_META = _get_corpora_meta(GLOBAL_CONFIG.get("corpora_file"))
    CORPORA, INITIAL_TABLES, CORPORA_CONFIGS = _get_corpora(CORPUS_META)
    
    # this can potentially save time: generate layouts for all datasets
    # before the pages are visited. comes at expense of some memory,
    # but the app should obviously be able to handle all datasets in use
    if GLOBAL_CONFIG["load_layouts"]:
        for corpus in CORPUS_META:
            if not corpus.disabled:
                load_layout(corpus.slug, set_and_register=False)


