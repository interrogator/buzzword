"""
buzzword explorer: run on startup, corpus loading and app initialisation
"""


import json
import os

import pandas as pd

from buzz.corpus import Collection
from buzz.constants import LANGUAGES, AVAILABLE_MODELS

from django_plotly_dash import DjangoDash

from django.conf import settings
from django.db import IntegrityError

from .helpers import (
    _get_corpus,
    _postprocess_corpus,
    register_callbacks,
    _add_links,
    _update_frequencies
)


def _load_languages():
    """
    Put all available languages into the DB
    """
    choices = [(k, v) for k, v in sorted(LANGUAGES.items()) if v in AVAILABLE_MODELS]
    print(f"Loading languages: {', '.join([i[0] for i in choices])}...")
    from explore.models import Language
    for longname, short in choices:
        try:
            Language(name=longname, short=short).save()
        # IntegrityError: already exists, don't care
        # OperationalError: models aren't yet populated (on first run)
        except IntegrityError:
            pass


def _load_corpora():
    """
    Load contents of corpora.json into DB as Corpus objects
    """
    from explore.models import Corpus
    corpora_file = os.path.abspath(settings.CORPORA_FILE)
    print(f"Loading corpora, using corpus configuration at: {corpora_file}")
    with open(corpora_file) as fo:
        data = json.load(fo)
    for name, meta in data.items():
        modelled = Corpus.from_json(meta, name)
        print(f"Saving corpus model to DB: {modelled.slug}")
        modelled.save()


def _get_or_load_corpora(slug=None, force=False):
    try:
        if force:
            raise Exception("You should never see this error.")
        from start.apps import corpora, initial_tables, initial_concs
        if corpora:
            return corpora, initial_tables, initial_concs
        else:
            raise ValueError("Data not loaded yet.")
    except:
        corpora = dict()
        initial_tables = dict()
        initial_concs = dict()
        corpora_file = os.path.abspath(settings.CORPORA_FILE)
        print(f"* Loading corpora, using corpus configuration at: {corpora_file}")
        with open(corpora_file) as fo:
            data = json.load(fo)
        for name, meta in data.items():
            if (slug or force) and meta["slug"] != slug:
                continue
            corpus = Collection(meta["path"])
            if not corpus.conllu:
                print(f"No parsed data at {corpus.path}")
                continue
            corpus = corpus.conllu.load(multiprocess=False)
            corpora[meta["slug"]] = corpus
            try:
                display = meta["initial_table"]
                assert isinstance(display, dict)
            except:
                display = dict(show="p", subcorpora="year")
            print(f"* Generating an initial table for {name} using {display}")
            initial_table = corpus.table(**display)
            initial_table = initial_table.drop("file", axis=1, errors="ignore")
            initial_tables[meta["slug"]] = initial_table

            try:
                search = json.loads(corpus["initial_query"])
            except:
                search = {"target": "x", "query": "NOUN"}
            result = getattr(corpus.just, search["target"])(search["query"])

            met = ["file", "s", "i"]
            if isinstance(corpus, pd.DataFrame):
                for feat in {"speaker", "year"}:
                    if feat in corpus.columns:
                        met.append(feat)
            print(f"* Generating initial conc for {name} using {search}")
            conc = result.conc(n=settings.MAX_CONC, metadata=met, window=(100, 100))
            conc["file"] = conc["file"].apply(os.path.basename)
            conc["file"] = conc["file"].str.replace(".conllu", "", regex=False)
            if meta["pdfs"]:
                conc = _add_links(conc, slug=meta["slug"], conc=True)
            initial_concs[meta["slug"]] = conc
        return corpora, initial_tables, initial_concs


def _load_explorer_data(multiprocess=False):
    """
    Load in all available corpora and make their initial tables

    This is run when the app starts up
    """
    from explore.models import Corpus
    corpora = dict()
    initial_tables = dict()
    for corpus in Corpus.objects.all():
        if corpus.disabled:
            print(f"Skipping corpus because it is disabled: {corpus.name}")
            continue

        buzz_collection = Collection(corpus.path)
        # a corpus must have a feather or conll to be explorable. prefer feather.
        buzz_corpus = buzz_collection.feather or buzz_collection.conllu

        if buzz_corpus is None:
            print(f"No parsed data found for {corpus.path}")
            continue
        
        # corpora[corpus.slug] = buzz_corpus

        if corpus.load:
            print(f"Loading corpus into memory: {corpus.name} ...")
            opts = dict(add_governor=corpus.add_governor, multiprocess=multiprocess)
            buzz_corpus = buzz_corpus.load(**opts)
            print(f"Corpus ({len(buzz_corpus)} tokens): {corpus.name}")
            buzz_corpus = _postprocess_corpus(buzz_corpus, corpus)
            cols = json.loads(corpus.drop_columns)
            if cols:
                buzz_corpus = buzz_corpus.drop(cols, axis=1, errors="ignore")
            corpora[corpus.slug] = buzz_corpus
        else:
            print(f"NOT loading corpus into memory: {corpus.name} ...")

        # what should be shown in the frequencies space to begin with?
        if getattr(corpus, "initial_table", False):
            display = json.loads(corpus.initial_table)
        else:
            display = dict(show="p", subcorpora="year")
            print(f"Generating an initial table for {corpus.name} using {display}")
            initial_table = buzz_corpus.table(**display)
            initial_tables[corpus.slug] = initial_table

    return corpora, initial_tables


def load_layout(slug, spec=False, set_and_register=True, return_layout=False, force=False):
    """
    Django can import this function to set the correct dataset on explore page

    Return app instance, just in case django has a use for it.

    This is the function called by explore.view.explore
    """
    from .tabs import make_explore_page
    fullpath = os.path.abspath(settings.CORPORA_FILE)
    print(f"Using django corpus configuration at: {fullpath}")
    corpora, initial_tables, initial_concs = _get_or_load_corpora(slug, force=force)
    corpus = corpora[slug]
    table = initial_tables[slug]
    conc = initial_concs[slug]
    layout = make_explore_page(corpus, table, conc, slug, spec=spec)
    if return_layout:
        return layout
    if set_and_register:
        app.layout = layout
        register_callbacks()
    return app


def get_layout():
    """
    Wrapper to get layout
    """
    slug = settings.BUZZWORD_SPECIFIC_CORPUS
    return load_layout(slug, return_layout=True)


def load_explorer_app(force=False):
    """
    Triggered during runserver, reload
    """
    from explore.models import Corpus
    _load_languages()
    _load_corpora()
    _get_or_load_corpora(force=force)
    # this can potentially save time: generate layouts for all datasets
    # before the pages are visited. comes at expense of some memory,
    # but the app should obviously be able to handle all datasets in use
    if settings.LOAD_LAYOUTS:
        for corpus in Corpus.objects.all():
            if not corpus.disabled:
                load_layout(corpus.slug, set_and_register=True, force=force)


app = DjangoDash("buzzword", suppress_callback_exceptions=True)
app.layout = get_layout
