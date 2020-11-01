''' URLS for App issue, start with api/issue/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('require', views.require_issue),
    path('fix', views.fix_issue),
    path('return', views.return_issue),
    path('transfer', views.transfer_issue),

    path('handling', views.handling_list),
    path('waiting', views.waiting_list),
]
