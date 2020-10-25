''' URLS for App users, start with api/user/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('tree', views.tree),
    path('add', views.add)
]
