from django.contrib.auth.models import AbstractUser
from django.db import models

from main.text import page_slugs_list, pages
from jsonfield import JSONField


class User(AbstractUser):
    page_slug = models.CharField(default=page_slugs_list[0], max_length=128)
    json = JSONField(default={"pages_progress": {}})
    developer_mode = models.BooleanField(default=False)


class ListEmail(models.Model):
    email = models.EmailField()


class CodeEntry(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    input = models.TextField()
    output = models.TextField(null=True)
    source = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='code_entries', null=True)
    page_slug = models.CharField(max_length=128)
    step_name = models.CharField(max_length=128)
