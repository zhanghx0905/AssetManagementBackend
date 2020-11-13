''' user/models.py '''
from enum import Enum
from datetime import datetime, timedelta

import jwt
from django.contrib.auth.models import (AbstractUser, Permission)
from django.db import models

from app.settings import SECRET_KEY
from department.models import Department


class UserPermission(Enum):
    ''' 用户权限枚举类 '''
    IT = 'user.IT'
    ASSET = 'user.ASSET'
    SYSTEM = 'user.SYSTEM'


class User(AbstractUser):
    '''
    User
    '''
    # 基本信息
    username = models.CharField(max_length=30, primary_key=True, unique=True, verbose_name='用户名')
    department = models.ForeignKey(Department, verbose_name='部门',
                                   on_delete=models.SET(Department.root))

    # 状态
    active = models.BooleanField(auto_created=True, default=True)
    token = models.CharField(max_length=100, auto_created=True, default='', blank=True)

    def generate_jwt_token(self):
        ''' generate token '''
        token = jwt.encode({
            # expiration time
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),   # issued at
            'username': self.username
        }, SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')

    def gen_roles(self) -> list:
        ''' generate roles to deliver for a user '''
        role = []
        if self.has_perm(UserPermission.IT):
            role.append('IT')
        if self.has_perm(UserPermission.ASSET):
            role.append('ASSET')
        if self.has_perm(UserPermission.SYSTEM):
            role.append('SYSTEM')
        return role + ['STAFF']

    def set_roles(self, roles: list):
        ''' set roles/permissions for user '''
        self.user_permissions.clear()
        permissions = Permission.objects.filter(codename__in=roles)
        for per in permissions:
            self.user_permissions.add(per)

    @classmethod
    def admin(cls):
        ''' 返回超级用户 admin '''
        return cls.objects.get(username='admin')

    class Meta:
        permissions = (
            ('ASSET', '资产管理员'),
            ('SYSTEM', '系统管理员'),
            ('IT', 'IT管理员'),
        )
