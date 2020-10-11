''' URLS for App users, start with api/user/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('list', views.user_list),
    path('delete', views.user_delete),
    path('exist', views.user_exist),
    path('add', views.user_add),
    path('edit', views.user_edit)
]
