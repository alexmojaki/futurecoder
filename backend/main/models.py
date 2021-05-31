from django.db import models


class ListEmail(models.Model):
    email = models.EmailField()
