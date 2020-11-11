'''asset model'''
import queue
from datetime import datetime

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from simple_history.models import HistoricalRecords

from users.models import User
from department.models import Department


class AssetCategory(MPTTModel):
    '''Asset Category'''
    name = models.CharField(max_length=30, unique=True, verbose_name='资产分类')
    parent = TreeForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)

    @classmethod
    def root(cls):
        ''' 返回顶层类型 '''
        return cls.objects.first().get_root()


class Asset(MPTTModel):
    ''' asset model '''
    # 可变属性
    name = models.CharField(max_length=30, null=False, verbose_name='资产名称')
    description = models.CharField(max_length=150, verbose_name='简介',
                                   blank=True, default='')
    parent = TreeForeignKey('self', blank=True, null=True,
                            on_delete=models.SET_NULL, verbose_name='父资产')

    status_choices = [('IDLE', '闲置'),
                      ('IN_USE', '使用'),
                      ('IN_MAINTAIN', '维护'),
                      ('RETIRED', '清退'),
                      ('DELETED', '删除')]
    status = models.CharField(max_length=20, choices=status_choices, default='IDLE')
    owner = models.ForeignKey(User, verbose_name='挂账人',
                              on_delete=models.SET(User.admin))
    # 不可变属性
    value = models.IntegerField(verbose_name='价值', default=1)
    category = models.ForeignKey(AssetCategory, verbose_name='类别',
                                 on_delete=models.CASCADE, default=None)
    start_time = models.DateTimeField(verbose_name='录入时间', auto_now_add=True)
    service_life = models.IntegerField(verbose_name='使用年限', default=1)

    history = HistoricalRecords(excluded_fields=['start_time', 'service_life',
                                                 'category', 'value',
                                                 'lft', 'rght', 'level', 'tree_id', ])

    def get_entire_tree(self) -> list:
        ''' 层次遍历 获得由资产父子关系定义的整棵资产树 '''
        item_queue = queue.Queue()
        res = []
        item_queue.put(self.get_root())
        while not item_queue.empty():
            item: Asset = item_queue.get()
            res.append(item)
            if not item.is_leaf_node():
                children = item.get_children()
                for asset in children:
                    item_queue.put(asset)
        return res

    def save(self, *args, tree_update=False, **kwargs):
        ''' 在某些属性变化时，改变资产相关的父子资产 '''
        def do_update(asset: Asset):
            asset.owner = self.owner
            asset.status = self.status
            asset._change_reason = self._change_reason
            asset.save()

        if tree_update:  # 层次遍历更新整棵资产树
            tree_list = self.get_entire_tree()
            for asset in tree_list:
                do_update(asset)
        else:
            super().save(*args, **kwargs)

    def to_dict(self):
        ''' 将 Asset 对象按字段转换成字典 '''
        return {
            'nid': self.id,
            'name': self.name,
            'value': self.value,
            'now_value': self.now_value,
            'category': self.category.name,
            'description': self.description,
            'parent_id': '' if self.parent is None else self.parent.id,
            'parent': self.parent_formated,
            'children_': self.children_formated,
            'status': self.status,
            'owner': self.owner.username,
            'department': self.department.name,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'service_life': self.service_life,
            'custom': AssetCustomAttr.get_custom_attrs(self),
        }

    @property
    def department(self) -> Department:
        ''' 所属部门，即所属用户的部门 '''
        return self.owner.department

    @property
    def now_value(self) -> int:
        ''' 资产折旧后的价值
        被清退的资产价值为0
        '''
        if self.status == 'RETIRED':
            return 0
        now = datetime.now()
        elapsed_year = now.year - self.start_time.year
        depreciation_rate = max(self.service_life - elapsed_year, 0) / self.service_life
        return self.value * depreciation_rate

    @property
    def parent_formated(self) -> str:
        ''' 父资产 格式化为 资产名(资产id)'''
        return '无' if self.parent is None else str(self.parent)

    @property
    def children_formated(self):
        ''' 格式化的子资产 '''
        if self.is_leaf_node():
            return '无'
        children = self.get_children()
        return ','.join(str(child) for child in children)

    def get_asset_manager(self):
        '''
        获得本资产的管理员

        如果本部门没有资产管理员，则自部门树向上遍历，直至顶层部门
        '''
        departments = self.department.get_ancestors(ascending=True, include_self=True)
        manager = None
        for department in departments:  # 自部门树向上遍历
            manager = department.get_asset_manager()
            if manager is not None:
                break
        return manager

    def __str__(self) -> str:
        return f'{self.name}(id={self.id})'


class CustomAttr(models.Model):
    ''' custom defined attribute '''
    name = models.CharField(max_length=20, verbose_name='属性名', primary_key=True)


class AssetCustomAttr(models.Model):
    ''' custom defined attribute linked with Asset '''
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    key = models.ForeignKey(CustomAttr, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name='属性值')

    @classmethod
    def get_custom_attr(cls, asset: Asset, key: CustomAttr) -> str:
        ''' 得到asset的某个自定义属性key的值，如果没有，就创建一个空的 '''
        try:
            return cls.objects.get(key=key, asset=asset).value
        except cls.DoesNotExist:
            cls.objects.create(asset=asset, key=key, value='')
            return ''

    @classmethod
    def get_custom_attrs(cls, asset: Asset) -> dict:
        ''' 得到asset的所有自定义属性 '''
        keys = CustomAttr.objects.all()
        res = {key.name: cls.get_custom_attr(asset, key) for key in keys}
        return res

    @classmethod
    def update_custom_attrs(cls, asset: Asset, kwargs: dict):
        ''' 更新 asset 的自定义属性 '''
        keys = CustomAttr.objects.all()
        for key in keys:
            try:
                attr = cls.objects.get(asset=asset, key=key)
                attr.value = kwargs.get(key.name, '')
                attr.save()
            except cls.DoesNotExist:
                cls.objects.create(asset=asset, key=key, value=kwargs.get(key.name, ''))

    @classmethod
    def search_custom_attr(cls, attr_name: str, key: str, assets):
        ''' 根据自定义属性名和关键词搜索 返回资产列表'''
        attr = CustomAttr.objects.get(name=attr_name)
        attrs = AssetCustomAttr.objects.filter(key=attr,
                                               value__contains=key)
        assets = assets.filter(assetcustomattr__in=attrs)
        return assets
