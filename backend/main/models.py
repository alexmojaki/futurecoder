from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    step = models.CharField(default='first_expression', max_length=32)


class CodeEntry(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    input = models.TextField()
    output = models.TextField(null=True)
    source = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='code_entries', null=True)
    step = models.CharField(default='first_expression', max_length=32)
