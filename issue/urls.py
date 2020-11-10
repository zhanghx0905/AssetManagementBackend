''' URLS for App issue, start with api/issue/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('require-old', views.issue_require_old),
    path('require', views.issue_require),
    path('fix', views.issue_fix),
    path('return', views.issue_return),
    path('transfer', views.issue_transfer),
    path('handle', views.issue_handle),
    path('delete', views.issue_delete),

    path('handling', views.handling_list),
    path('waiting', views.waiting_list),
]
