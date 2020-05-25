from django.db import models
from martor.models import MartorField


class Post(models.Model):
    description = MartorField()
    commit_msg = models.CharField(max_length=200, blank=True)


class PDF(models.Model):
    class Meta:
        unique_together = ["slug", "num"]

    slug = models.SlugField(max_length=255, unique=False)
    path = models.TextField()
    name = models.CharField(max_length=200)
    num = models.IntegerField()
