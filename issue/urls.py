''' URLS for App issue, start with api/issue/ '''
from django.urls import path

from . import views

urlpatterns = [
    path('require', views.require),
    path('handling', views.handling_list),
]
