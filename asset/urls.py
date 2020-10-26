''' URLS for App asset, start with api/asset/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('list', views.asset_list),
    path('add', views.asset_add),
    path('edit', views.asset_edit),
    path('category', views.category_tree),
    path('history', views.asset_history),
]
