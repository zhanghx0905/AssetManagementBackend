'''asset/app.py'''
from django.apps import AppConfig
from django.db.utils import OperationalError, IntegrityError


def init_category():
    '''初始化资产分类'''
    from .models import AssetCategory
    try:
        if not AssetCategory.objects.filter(name='资产'):
            root = AssetCategory(name='资产', parent=None)
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
    except OperationalError:
        pass
    except IntegrityError:
        pass


class AssetConfig(AppConfig):
    ''' asset config'''
    name = 'asset'

    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        init_category()
