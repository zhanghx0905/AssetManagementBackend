''' users/models.py '''

from datetime import datetime, timedelta

import jwt
from django.db import models

from app.settings import SECRET_KEY


class User(models.Model):
    '''
    The password attribute of a User object is a string in this format:
    <algorithm>$<iterations>$<salt>$<hash>
    '''
    # 基本信息
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=100)
    department = models.CharField(max_length=30, default='')

    # 权限
    is_asset_manager = models.BooleanField(default=False)
    is_system_manager = models.BooleanField(default=False)
    is_it_manager = models.BooleanField(default=False)

    # 状态
    is_active = models.BooleanField(auto_created=True, default=True)
    token = models.CharField(max_length=100, auto_created=True, default='', blank=True)

    def __str__(self) -> str:
        return self.username

    def generate_jwt_token(self):
        ''' generate token '''
        token = jwt.encode({
            # expiration time
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),   # issued at
            'username': self.username
        }, SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')
