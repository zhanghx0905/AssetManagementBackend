''' user/apps.py '''
from django.apps import AppConfig
from django.db.utils import IntegrityError, OperationalError


def init_department():
    ''' 增加顶层部门 '''
    from department.models import Department

    if not Department.objects.all().exists():
        top = Department(name='总公司', parent=None)
        top.save()

        d_1 = Department(name='开发部', parent=top)
        d_11 = Department(name='前端组', parent=d_1)
        d_12 = Department(name='后端组', parent=d_1)

        d_2 = Department(name='市场部', parent=top)
        d_3 = Department(name='运维部', parent=top)
        d_4 = Department(name='人力资源部', parent=top)
        d_5 = Department(name='财务部', parent=top)

        for department in [d_1, d_11, d_12, d_2, d_3, d_4, d_5]:
            department.save()


def add_admin():
    ''' 增加用户名密码均为 admin 的超级用户 '''
    from department.models import Department
    from .models import User
    if not User.objects.filter(username='admin').exists():
        admin = User(username='admin', department=Department.root(), is_superuser=True)
        admin.set_password('admin')
        admin.save()


def init_category():
    ''' 添加资产类别'''
    from asset.models import AssetCategory

    if not AssetCategory.objects.all().exists():
        root = AssetCategory(name='通用设备', parent=None)
        root.save()

        c_1 = AssetCategory(name='电子设备', parent=root)
        c_11 = AssetCategory(name='计算机设备', parent=c_1)
        c_12 = AssetCategory(name='办公设备', parent=c_1)
        c_13 = AssetCategory(name='通信设备', parent=c_1)
        c_2 = AssetCategory(name='电器设备', parent=root)
        c_21 = AssetCategory(name='生活电器', parent=c_2)
        c_22 = AssetCategory(name='会议会客电器', parent=c_2)
        c_3 = AssetCategory(name='仪器设备', parent=root)
        for cate in (c_1, c_11, c_12, c_13, c_2, c_21, c_22, c_3):
            cate.save()


def add_old_asset():
    ''' 增加一个旧资产，以展示资产折旧 '''
    from asset.models import Asset, AssetCategory
    from user.models import User
    from datetime import timedelta
    if not Asset.objects.all().exists():
        asset = Asset(name='旧资产',
                      value=10000,
                      category=AssetCategory.root(),
                      status='IDLE',
                      service_life=10,
                      owner=User.admin())
        asset.save()
        asset.start_time -= timedelta(366)
        asset.save()


class UserConfig(AppConfig):
    ''' UsersConfig '''
    name = 'user'

    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        try:  # 在数据表创建前调用会引发错误
            init_department()
            add_admin()
            init_category()
            # 增加一些非必须数据，测试用
            add_old_asset()
        except (OperationalError, IntegrityError):
            pass
