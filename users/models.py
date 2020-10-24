''' users/models.py '''

from datetime import datetime, timedelta

import jwt
from django.contrib.auth.models import (AbstractBaseUser, Permission,
                                        PermissionsMixin)
from django.db import models

from app.settings import SECRET_KEY



class User(AbstractBaseUser, PermissionsMixin):
    '''
    The password attribute of a User object is a string in this format:
    <algorithm>$<iterations>$<salt>$<hash>
    '''
    # 基本信息
    username = models.CharField(max_length=30, unique=True, verbose_name='用户名')
    department = models.CharField(max_length=30, default='', verbose_name='部门')

    # 状态
    active = models.BooleanField(auto_created=True, default=True)
    token = models.CharField(
        max_length=100, auto_created=True, default='', blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

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
        if self.has_perm('users.IT'):
            role.append('IT')
        if self.has_perm('users.ASSET'):
            role.append('ASSET')
        if self.has_perm('users.SYSTEM'):
            role.append('SYSTEM')
        return role + ['STAFF']

    def set_roles(self, roles: list):
        ''' set roles/permissions for user '''
        self.user_permissions.clear()
        permissions = Permission.objects.filter(codename__in=roles)
        for per in permissions:
            self.user_permissions.add(per)

    class Meta:
        permissions = (
            ('ASSET', '资产管理员'),
            ('SYSTEM', '系统管理员'),
            ('IT', 'IT管理员'),
        )


