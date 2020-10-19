''' users/apps.py '''
from django.apps import AppConfig
from django.contrib.auth.hashers import make_password


def add_admin():
    ''' 增加用户名密码均为 admin 的超级用户 '''
    from .models import User
    if not User.objects.filter(username='admin'):
        admin = User(username='admin',
                     password=make_password('admin', None),
                     is_asset_manager=True,
                     is_it_manager=True,
                     is_system_manager=True)
        admin.save()


class UsersConfig(AppConfig):
    ''' UsersConfig '''
    name = 'users'

    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        add_admin()
