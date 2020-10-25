'''model definition of department based on mptt'''
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Department(MPTTModel):
    ''' department of an employer'''
    name = models.CharField(max_length=30, verbose_name='部门名称')
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)

    @classmethod
    def root(cls):
        ''' return the root of the tree'''
        return cls.objects.first().get_root()
