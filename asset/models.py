'''asset model'''
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
    name = models.CharField(max_length=30, null=False, verbose_name='资产名称')
    quantity = models.IntegerField(verbose_name='数量', default=1)
    value = models.IntegerField(verbose_name='价值', default=1)

    category = models.ForeignKey(AssetCategory, verbose_name='类别',
                                 on_delete=models.CASCADE, default=None)
    ty_choices = [('ITEM', '价值型'), ('AMOUNT', '数量型')]
    type_name = models.CharField(verbose_name='资产类型', choices=ty_choices,
                                 max_length=20, default='ITEM')

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
    start_time = models.DateTimeField(verbose_name='录入时间', auto_now_add=True)
    service_life = models.IntegerField(verbose_name='使用年限', default=1)

    owner = models.ForeignKey(User, verbose_name='挂账人',
                              on_delete=models.SET(User.admin))

    history = HistoricalRecords(excluded_fields=['start_time', 'lft', 'rght', 'level', 'tree_id'])

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
        if elapsed_year >= self.service_life:
            return 0
        depreciation_rate = (self.service_life - elapsed_year) / self.service_life
        return self.value * depreciation_rate

    @property
    def parent_id_(self):
        ''' 返回父资产 id '''
        if self.parent is None:
            return ''
        return self.parent.id

    @property
    def parent_formated(self) -> str:
        ''' 父资产 格式化为 资产名(资产id)'''
        if self.parent is None:
            return '无'
        parent = self.parent
        return f'{parent.name}({parent.id})'

    @property
    def children(self):
        ''' 子资产 Query Set '''
        return self.__class__.objects.filter(parent=self)

    @property
    def children_formated(self):
        ''' 格式化的子资产 '''
        children = self.children
        if not children.exists():
            return '无'
        res = [f"{child.name}({child.id})" for child in children]
        return ','.join(res)

    def get_asset_manager(self) -> User:
        ''' 获得本资产的管理员 '''
        departments = self.department.get_ancestors(ascending=True, include_self=True)
        for department in departments:  # 自部门树向上遍历
            users = User.objects.filter(department=department)
            for user in users:  # 随机找一个资产管理员
                if user.has_perm('user.ASSET'):
                    return user
        return User.admin()


class CustomAttr(models.Model):
    ''' custom - defined attribute '''
    name = models.CharField(max_length=20, verbose_name='属性名', primary_key=True)


class AssetCustomAttr(models.Model):
    ''' custom - defined attribute linked with Asset '''
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    key = models.ForeignKey(CustomAttr, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name='属性值')

    @classmethod
    def get_custom_attr(cls, asset, key) -> str:
        ''' 得到asset的某个自定义属性key的值 '''
        try:
            val = cls.objects.get(key__name=key, asset=asset).value
        except cls.DoesNotExist:
            val = ''
        return val
