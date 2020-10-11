from django.db import models


class User(models.Model):
    '''
    The password attribute of a User object is a string in this format:
    <algorithm>$<iterations>$<salt>$<hash>
    '''
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=100)
    department = models.CharField(max_length=30, default='')
    is_asset_manager = models.BooleanField(default=False)
    is_system_manager = models.BooleanField(default=False)
    is_it_manager = models.BooleanField(default=False)
    # activated = models.BooleanField(auto_created=True, default=True)
