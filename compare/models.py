from django.db import models
from martor.models import MartorField


class Post(models.Model):
    description = MartorField(blank=True)
    commit_msg = models.CharField(max_length=200, blank=True)


class PDF(models.Model):
    class Meta:
        unique_together = ["slug", "num"]

    slug = models.SlugField(max_length=255, unique=False)
    path = models.TextField()
    name = models.CharField(max_length=200)
    num = models.IntegerField()


class TIF(models.Model):
    class Meta:
        unique_together = ["slug", "num"]

    slug = models.SlugField(max_length=255, unique=False)
    path = models.TextField()
    name = models.CharField(max_length=200)
    num = models.IntegerField()


class OCRUpdate(models.Model):
    class Meta:
        unique_together = ["slug", "timestamp", "pdf"]

    slug = models.SlugField(max_length=255, unique=False)
    commit_msg = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    previous = models.TextField()
    text = models.TextField()
    pdf = models.ForeignKey(PDF, on_delete=models.PROTECT)
