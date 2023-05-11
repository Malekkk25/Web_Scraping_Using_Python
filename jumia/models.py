from django.db import models

#nombre des pages pour la pagination
class Number(models.Model):
    value = models.IntegerField()
