'''包含模型初始化操作'''
from django.apps import AppConfig
from django.db.utils import OperationalError


def init_department():
    '''设置初始部门层级'''
    from .models import Department
    try:
        Department.objects.all().delete()
        department1 = Department(name='d1', parent=None)
        department2 = Department(name='d2', parent=department1)
        department3 = Department(name='d3', parent=department1)
        department4 = Department(name='d4', parent=department2)
        department5 = Department(name='d5', parent=department2)
        department1.save()
        department2.save()
        department3.save()
        department4.save()
        department5.save()
    except OperationalError:
        pass


class DepartmentConfig(AppConfig):
    '''department config'''
    name = 'department'

    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        init_department()
