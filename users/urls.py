from django.urls import path

from . import views

urlpatterns = [
    path('register', views.user_register),
    path('login', views.user_login),
    path('me', views.user_info)
]