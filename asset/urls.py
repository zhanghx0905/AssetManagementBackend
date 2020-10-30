''' URLS for App asset, start with api/asset/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('list', views.asset_list),
    path('add', views.asset_add),
    path('edit', views.asset_edit),
    path('history', views.asset_history),
    path('require', views.asset_require),

    path('category', views.category_tree),
    path('category/delete', views.category_delete),
    path('category/add', views.category_add),
    path('category/edit', views.category_edit),
]
