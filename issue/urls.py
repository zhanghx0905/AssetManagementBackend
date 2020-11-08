''' URLS for App issue, start with api/issue/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('require', views.issue_require),
    path('require-new', views.issue_require_new),
    path('fix', views.issue_fix),
    path('return', views.issue_return),
    path('transfer', views.issue_transfer),
    path('handle', views.issue_handle),
    path('delete', views.issue_delete),

    path('handling', views.handling_list),
    path('waiting', views.waiting_list),
]
