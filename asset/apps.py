'''asset/app.py'''
from django.apps import AppConfig
from django.db.utils import OperationalError


def init_catagory():
    '''初始化资产分类'''
    from .models import AssetCatagory
    try:
        root = AssetCatagory(name='资产', parent=None)
        c_1 = AssetCatagory(name='电子设备', parent=root)
        c_11 = AssetCatagory(name='计算机设备', parent=c_1)
        c_12 = AssetCatagory(name='办公设备', parent=c_1)
        c_13 = AssetCatagory(name='通信设备', parent=c_1)
        c_2 = AssetCatagory(name='电器设备', parent=root)
        c_21 = AssetCatagory(name='生活电器', parent=c_2)
        c_22 = AssetCatagory(name='会议会客电器', parent=c_2)
        c_3 = AssetCatagory(name='仪器设备', parent=root)
        for cata in (root, c_1, c_11, c_12, c_13, c_2, c_21, c_22, c_3):
            cata.save()
    except OperationalError:
        pass

class AssetConfig(AppConfig):
    ''' asset config'''
    name = 'asset'
    def ready(self) -> None:
        ''' 在子类中重写此方法，以便在Django启动时运行代码。 '''
        super().ready()
        init_catagory()
