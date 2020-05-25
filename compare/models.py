from django.db import models
from martor.models import MartorField


class Post(models.Model):
    title = models.CharField(max_length=200)
    description = MartorField()
    wiki = MartorField()


class PDF(models.Model):
    class Meta:
        unique_together = ["slug", "num"]

    slug = models.SlugField(max_length=255, unique=False)
    path = models.TextField()
    name = models.CharField(max_length=200)
    num = models.IntegerField()
