import datetime
import json

from buzz.constants import LANGUAGES, AVAILABLE_MODELS
from django.db import models
from explorer.strings import _slug_from_name

from django.db import IntegrityError
from django.contrib.auth import get_user_model

# get language choices from buzz. we use benepar because SPACY_LANGUAGES
# contains information about which parser model to use, we don't want that
LANGUAGE_CHOICES = [
    (v, k) for k, v in sorted(LANGUAGES.items()) if v in AVAILABLE_MODELS
]


def _string_or_none(jsonfield):
    if not jsonfield:
        return
    return json.dumps(jsonfield)


class Language(models.Model):
    short = models.CharField(max_length=10)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Corpus(models.Model):
    class Meta:
        verbose_name_plural = "Corpora"  # can't tolerate "Corpuss"

    slug = models.SlugField(
        max_length=255, unique=True
    )  # this can't be null because a name needs to exist
    name = models.CharField(max_length=255)
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, choices=LANGUAGE_CHOICES
    )
    path = models.TextField()
    desc = models.TextField(default="", blank=True)
    add_governor = models.BooleanField(null=True)
    disabled = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    load = models.BooleanField(default=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    initial_query = models.TextField(null=True, blank=True)
    initial_table = models.TextField(null=True, blank=True)
    drop_columns = models.TextField(null=True, blank=True)
    parsed = models.BooleanField(default=False)
    pdfs = models.BooleanField(null=True, default=False)
    example_concordance = models.CharField(null=True, blank=True, max_length=30)
    epub = models.BooleanField(null=True, default=False)

    @classmethod
    def from_json(cls, jsondata, corpus_name):
        slug = jsondata.get("slug", _slug_from_name(corpus_name))
        try:
            corp = cls.objects.get(slug=slug)
            return corp
        except cls.DoesNotExist:
            pass
        language = Language.objects.get(short=jsondata.get("language"))
        path = jsondata.get("path")
        desc = jsondata.get("desc", "")
        disabled = jsondata.get("disabled", False)
        date = datetime.datetime.strptime(jsondata.get("date", "1900"), "%Y").date()
        load = jsondata.get("load", True)
        url = jsondata.get("url")
        pdfs = jsondata.get("pdfs")
        initial_query = _string_or_none(jsondata.get("initial_query"))
        initial_table = _string_or_none(jsondata.get("initial_table"))
        drop_columns = _string_or_none(jsondata.get("drop_columns"))
        example_concordance = _string_or_none(jsondata.get("example_concordance"))
        epub = jsondata.get("epub")

        has_error = False
        if not path:
            has_error = True
            # logging.error("no path = no good")
        if not language:
            has_error = True
            # logging.error("language missing")
        if has_error:
            raise Exception(
                "some problem with loading corpus from json. check error log"
            )

        corp = Corpus(
            name=corpus_name,
            slug=slug,
            language=language,
            path=path,
            desc=desc,
            disabled=disabled,
            date=date,
            load=load,
            url=url,
            initial_query=initial_query,
            initial_table=initial_table,
            parsed=True,  # assuming all files provided this way are already parsed
            pdfs=pdfs,
            drop_columns=drop_columns,
            example_concordance=example_concordance,
            epub=epub
        )
        corp.save()

        return corp


class SearchResult(models.Model):
    """
    Model a search result in the explorer interface
    """
    class Meta:
        unique_together = ["slug", "user", "idx"]

    # corpus = models.ForeignKey(Corpus, on_delete=models.SET_NULL)
    slug = models.SlugField(max_length=255)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    indices = models.TextField()
    position = models.TextField(null=True)
    query = models.CharField(max_length=300)
    regex = models.BooleanField()
    target = models.CharField(max_length=50)
    inverse = models.BooleanField()
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True)
    idx = models.IntegerField()
    name = models.CharField(max_length=255, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField()

class TableResult(models.Model):

    class Meta:
        unique_together = ["slug", "user", "idx"]

    slug = models.SlugField(max_length=255)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    idx = models.IntegerField()
    produced_from = models.ForeignKey(SearchResult, on_delete=models.SET_NULL, null=True)
    show = models.CharField(max_length=300)
    subcorpora = models.CharField(max_length=300)
    relative = models.CharField(max_length=20, null=True)
    keyness = models.CharField(max_length=2, null=True)
    sort = models.CharField(max_length=10, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
