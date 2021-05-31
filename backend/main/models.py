from django.contrib.auth.models import AbstractUser
from django.db import models

from core.text import page_slugs_list
from jsonfield import JSONField


class User(AbstractUser):
    page_slug = models.CharField(default=page_slugs_list[0], max_length=128)
    json = JSONField(default={"pages_progress": {}})
    developer_mode = models.BooleanField(default=False)


class ListEmail(models.Model):
    email = models.EmailField()
