'''包含模型初始化操作'''
from django.apps import AppConfig
from django.db.utils import OperationalError


def init_department():
    '''设置初始部门层级'''
    from .models import Department
    try:
        if not Department.objects.filter(name='部门'):
            top_department = Department(name='部门', parent=None)
            top_department.save()
    except OperationalError:
        pass


class DepartmentConfig(AppConfig):
    '''department config'''
    name = 'department'

    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        init_department()
