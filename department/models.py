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

    def get_asset_manager(self):
        ''' 获得本部门的资产管理员 '''
        from user.models import User, UserPermission
        user = User.objects.filter(department=self)
        for user in user:  # 随机找一个资产管理员
            if user.has_perm(UserPermission.ASSET):
                return user
        return None
