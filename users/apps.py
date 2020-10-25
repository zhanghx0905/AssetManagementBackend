''' users/apps.py '''
from django.apps import AppConfig
from django.db.utils import OperationalError

def init_department():
    '''设置初始部门层级'''
    from department.models import Department
    try:
        if not Department.objects.filter(name='部门').exists():
            top_department = Department(name='部门', parent=None)
            top_department.save()
    except OperationalError:
        pass

def add_admin():
    ''' 增加用户名密码均为 admin 的超级用户 '''
    from department.models import Department
    from .models import User
    try:    # 防止在数据表创建前调用，引发错误
        root = Department.root()
        if not User.objects.filter(username='admin').exists():
            admin = User(username='admin', department=root)
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
        init_department()
        add_admin()
