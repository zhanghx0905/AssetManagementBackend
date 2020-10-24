from django.apps import AppConfig
from django.db.utils import OperationalError

def init_department():
    '''设置初始部门层级'''
    from .models import Department
    try:
        Department.objects.all().delete()
        d1 = Department(name='d1', parent=None)
        d2 = Department(name='d2', parent=d1)
        d3 = Department(name='d3', parent=d1)
        d4 = Department(name='d4', parent=d2)
        d5 = Department(name='d5', parent=d2)
        d1.save()
        d2.save()
        d3.save()
        d4.save()
        d5.save()
    except OperationalError:
        pass

class DepartmentConfig(AppConfig):
    name = 'department'

    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        init_department()