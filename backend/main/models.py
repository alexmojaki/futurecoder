from django.contrib.auth.models import AbstractUser
from django.db import models

from main.text import page_slugs_list, pages


class User(AbstractUser):
    page_slug = models.CharField(default=page_slugs_list[0], max_length=128)
    step_name = models.CharField(default=pages[page_slugs_list[0]].step_names[0], max_length=128)
    developer_mode = models.BooleanField(default=False)

    @property
    def page(self):
        return pages[self.page_slug]

    @property
    def step(self):
        return getattr(self.page, self.step_name)


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
