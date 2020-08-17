from django.contrib.auth.models import AbstractUser
from django.db import models

from main.text import page_slugs_list, pages
from jsonfield import JSONField


class PagesProgress(dict):
    """Supplies the first step name as the default for missing pages"""
    def __missing__(self, key):
        result = {"step_name": pages[key].step_names[0]}
        self[key] = result
        return result


class User(AbstractUser):
    page_slug = models.CharField(default=page_slugs_list[0], max_length=128)
    json = JSONField(default={"pages_progress": {}})
    developer_mode = models.BooleanField(default=False)

    @property
    def pages_progress(self):
        """
        Returns a PagesProgress dict which fills in default values.
        Ensures the result is directly in the json field so changes
        are written back to the database.
        """
        result = self.json["pages_progress"]
        if not isinstance(result, PagesProgress):
            result = self.json["pages_progress"] = PagesProgress(result)
        return result

    @property
    def page(self):
        return pages[self.page_slug]


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
