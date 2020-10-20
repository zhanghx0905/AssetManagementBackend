'''asset model'''

from django.db import models

# Create your models here.

class Asset(models.Model):
    ''' asset model '''
    nid = models.CharField(max_length=20, unique=True, verbose_name='nid')
    name = models.CharField(max_length=30, unique=False, verbose_name='用户名')
