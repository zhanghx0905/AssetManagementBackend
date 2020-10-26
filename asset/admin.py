''' asset/admin.py '''
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Asset, AssetCategory


class AssetHistoryAdmin(SimpleHistoryAdmin):
    ''' 将simple_history集成到Django Admin '''
    list_display = ['name', 'status', 'owner', 'history']


admin.site.register(Asset, AssetHistoryAdmin)
admin.site.register(AssetCategory)
