'''model definition of department based on mptt'''
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.


class Department(MPTTModel):
    ''' department of an employer'''
    department_id = models.AutoField(
        primary_key=True, max_length=20, unique=True, verbose_name='id')
    name = models.CharField(max_length=30, verbose_name='部门名称')
    parent = TreeForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)
