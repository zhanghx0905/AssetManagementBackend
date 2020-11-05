''' users/apps.py '''
from django.apps import AppConfig
from django.db.utils import IntegrityError, OperationalError


def init_department():
    '''设置初始部门层级'''
    from department.models import Department

    if not Department.objects.filter(name='部门').exists():
        top_department = Department(name='部门', parent=None)
        top_department.save()
        for i in range(2):
            department = Department(name=f'子部门{i}', parent=top_department)
            department.save()


def add_admin():
    ''' 增加用户名密码均为 admin 的超级用户 '''
    from department.models import Department
    from .models import User
    root = Department.root()
    if not User.objects.filter(username='admin').exists():
        admin = User(username='admin', department=root, is_superuser=True)
        admin.set_password('admin')
        admin.save()


def add_old_asset():
    ''' 增加一个旧资产，以展示资产折旧 '''
    from asset.models import Asset, AssetCategory
    from users.models import User
    from datetime import timedelta
    try:
        if not Asset.objects.filter(name='旧资产').exists():
            asset = Asset(name='旧资产',
                          quantity=1,
                          value=10000,
                          category=AssetCategory.root(),
                          status='IDLE',
                          service_life=10,
                          owner=User.admin())
            asset.save()
            asset.start_time -= timedelta(366)
            asset.save()
    except OperationalError:
        pass


class UsersConfig(AppConfig):
    ''' UsersConfig '''
    name = 'users'

    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        try:  # 在数据表创建前调用会引发错误
            init_department()
            add_admin()
            add_old_asset()
        except (OperationalError, IntegrityError):
            pass
