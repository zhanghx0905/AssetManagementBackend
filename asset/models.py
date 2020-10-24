'''asset model'''

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.


class Asset(models.Model):
    ''' asset model '''

    nid = models.AutoField(primary_key=True, max_length=20,
                           unique=True, verbose_name='nid')
    name = models.CharField(max_length=30, null=False, verbose_name='资产名称')
    quantity = models.IntegerField(verbose_name='数量', default=1)
    value = models.IntegerField(verbose_name='资产价值', default=1)
    is_quantity = models.BooleanField(verbose_name='资产类型', default=False)
    description = models.CharField(
        max_length=50, verbose_name='简介', blank=True, default='')
    parent = models.CharField(
        max_length=20, verbose_name='父资产', blank=True, default='')
    child = models.CharField(
        max_length=100, verbose_name='子资产', blank=True, default='')

    status_choices = [('IDLE', 'idle'),
                      ('IN_USE', 'in_use'),
                      ('IN_MAINTAIN', 'in_maintain'),
                      ('RETIRED', 'retired'),
                      ('DELETED', 'deleted')]

    status = models.CharField(
        max_length=20, choices=status_choices, default='IDLE')

    owner = models.CharField(max_length=30, verbose_name='挂账人', default='')
    department = models.CharField(max_length=30, verbose_name='部门', default='')
    start_time = models.DateTimeField(verbose_name='录入时间', null=True)


class AssetCatagory(MPTTModel):
    '''Asset Catagory'''
    name = models.CharField(max_length=30, verbose_name='资产分类')
    parent = TreeForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)
    