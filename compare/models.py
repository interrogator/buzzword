from django.db import models
from martor.models import MartorField
from django.contrib.auth import get_user_model

class Post(models.Model):
    description = MartorField(blank=True)
    commit_msg = models.CharField(max_length=200, blank=True)


class PDF(models.Model):
    class Meta:
        unique_together = ["slug", "num"]
        verbose_name_plural = "PDFs"
        verbose_name = "PDF"

    slug = models.SlugField(max_length=255, unique=False)
    path = models.TextField()
    name = models.CharField(max_length=200)
    num = models.IntegerField()


class TIF(models.Model):
    class Meta:
        unique_together = ["slug", "num"]
        verbose_name_plural = "TIFs"
        verbose_name = "TIF"

    slug = models.SlugField(max_length=255, unique=False)
    path = models.TextField()
    name = models.CharField(max_length=200)
    num = models.IntegerField()


class OCRUpdate(models.Model):
    class Meta:
        unique_together = ["slug", "timestamp", "pdf"]
        verbose_name_plural = "OCR texts"
        verbose_name = "OCR texts"

    slug = models.SlugField(max_length=255, unique=False)
    commit_msg = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    previous = models.TextField()
    text = models.TextField()
    pdf = models.ForeignKey(PDF, on_delete=models.PROTECT)
    username = models.CharField(max_length=200, blank=False, unique=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    accepted = models.BooleanField(default=False)
