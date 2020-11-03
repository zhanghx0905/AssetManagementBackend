"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from . import views


urlpatterns = [
    path('api/user/', include(('users.urls', '用户'), namespace='用户')),
    path('api/asset/', include(('asset.urls', '资产'), namespace='资产')),
    path('api/department/', include(('department.urls', '部门'), namespace='部门')),
    path('api/issue/', include(('issue.urls', '事项'), namespace='事项')),
    path('api/logs', views.get_logs),
    path('admin/', admin.site.urls),
]
