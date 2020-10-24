''' URLS for App asset, start with api/asset/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('list', views.asset_list),
    path('add', views.asset_add),
    path('edit', views.asset_edit),
    path('catagory', views.catagory_tree)
]
