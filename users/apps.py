''' users/apps.py '''
from django.apps import AppConfig
from django.db.utils import OperationalError


def add_admin():
    ''' 增加用户名密码均为 admin 的超级用户 '''
    from .models import User
    try:    # 防止在数据表创建前调用，引发错误
        if not User.objects.filter(username='admin'):
            admin = User(username='admin')
            admin.set_password('admin')
            admin.save()
            admin.set_roles(['IT', 'ASSET', "SYSTEM"])
            
    except OperationalError:
        pass


class UsersConfig(AppConfig):
    ''' UsersConfig '''
    name = 'users'

    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        add_admin()
