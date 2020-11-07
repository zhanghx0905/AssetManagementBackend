''' admin '''
from django.contrib import admin

from .models import Issue, RequireIssue

admin.register(Issue)
admin.register(RequireIssue)
