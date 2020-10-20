''' URLS for App asset, start with api/asset/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('list', views.asset_list),
]
