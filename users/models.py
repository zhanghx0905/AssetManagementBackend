from django.db import models


class User(models.Model):
    ''' 
    The password attribute of a User object is a string in this format:
    <algorithm>$<iterations>$<salt>$<hash>
    '''
    name = models.CharField(max_length=20, unique=True)
    pwd = models.CharField(max_length=100)
