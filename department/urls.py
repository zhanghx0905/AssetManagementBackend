''' URLS for App users, start with api/user/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('tree', views.department_tree),
    path('add', views.department_add),
    path('delete', views.department_delete),
    path('edit', views.department_edit)
]
