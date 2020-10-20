'''asset model'''

from django.db import models

# Create your models here.


class Asset(models.Model):
    ''' asset model '''
    nid = models.CharField(max_length=20, unique=True, verbose_name='nid')
    name = models.CharField(max_length=30, verbose_name='用户名')
    quantity = models.IntegerField(verbose_name='数量')
    is_quantity = models.BooleanField(verbose_name='资产类型')
    description = models.CharField(max_length=50, verbose_name='简介')
    parent = models.CharField(max_length=20, verbose_name='从属资产')
    