''' asset/admin.py '''
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Asset


class AssetHistoryAdmin(SimpleHistoryAdmin):
    ''' 将simple_history集成到Django Admin '''
    list_display = ['name', 'status', 'owner', 'changed_by']


admin.site.register(Asset, AssetHistoryAdmin)
