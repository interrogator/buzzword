import json
import datetime
from django.db import models

from explorer.parts.strings import _slug_from_name

def _string_or_none(jsonfield):
    if not jsonfield:
        return
    return json.dumps(jsonfield)

class Corpus(models.Model):
    class Meta:
        verbose_name_plural = "Corpora" # can't tolerate "Corpuss"

    slug = models.SlugField(
        max_length=255, unique=True
    )  # this can't be null because a name needs to exist
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=255)  # probably turn this into a model later
    path = models.TextField()
    desc = models.TextField(default="")
    length = models.BigIntegerField(null=True)
    add_governor = models.BooleanField(null=True)
    # drop_columns = array -> needs to be relation
    disabled = models.BooleanField(default=False)
    date = models.DateField(null=True)
    load = models.BooleanField(default=True)
    url = models.URLField(max_length=255, null=True)
    initial_query = models.TextField(null=True)
    initial_table = models.TextField(null=True)

    @classmethod
    def from_json(cls, jsondata, corpus_name):
        slug = jsondata.get("slug", _slug_from_name(corpus_name))
        try:
            corp = cls.objects.get(slug=slug)
            return corp
        except cls.DoesNotExist:
            pass
        language = jsondata.get("language")
        path = jsondata.get("path")
        desc = jsondata.get("desc", "")
        length = jsondata.get("length")
        disabled = jsondata.get("disabled", False)
        date = datetime.datetime.strptime(jsondata.get("date", "1900"), "%Y").date()
        load = jsondata.get("load", True)
        url = jsondata.get("url")
        initial_query = _string_or_none(jsondata.get("initial_query"))
        initial_table = _string_or_none(jsondata.get("initial_table"))

        has_error = False
        if not path:
            has_error = True
            logging.error("no path = no good")
        if not language:
            has_error = True
            logging.error("language missing")
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
            length=length,
            disabled=disabled,
            date=date,
            load=load,
            url=url,
            initial_query=initial_query,
            initial_table=initial_table,
        )
        corp.save()

        for drop_col in jsondata.get("drop_columns", []):
            col = DropColumn(corpus=corp, column_name=drop_col)
            col.save()

        return corp


class DropColumn(models.Model):
    corpus = models.ForeignKey(Corpus, on_delete=models.CASCADE)
    column_name = models.CharField(max_length=255)
