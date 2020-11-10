''' models for issue '''
from django.db import models

from users.models import User
from asset.models import Asset, AssetCategory


class AbstractIssue(models.Model):
    ''' Issue 基类 用于复用字段 '''
    # related 规避反向查询冲突
    initiator = models.ForeignKey(User, on_delete=models.CASCADE,
                                  verbose_name='发起者',
                                  related_name="%(app_label)s_%(class)s_initiator")
    handler = models.ForeignKey(User, on_delete=models.CASCADE,
                                verbose_name='处理者',
                                related_name='%(app_label)s_%(class)s_hanlder')

    status_choices = [
        ('DOING', '进行中'),
        ('SUCCESS', '成功'),
        ('FAIL', '失败'),
    ]
    status = models.CharField(max_length=10, choices=status_choices,
                              default='DOING', auto_created=True)

    def to_dict(self):
        ''' 转换成字典 '''
        return {
            'nid': self.id,
            'initiator': self.initiator.username,
            'status': self.status,
        }

    class Meta:
        abstract = True


class Issue(AbstractIssue):
    ''' Issue 数据类
    与单个资产关联的事项，包括维修，转移，退库 '''

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name='资产')

    # 用于涉及第三个用户的请求(转移)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE,
                                 verbose_name='被分配者',
                                 related_name='assignee',
                                 blank=True, null=True)
    type_choices = [
        ('REQUIRE', '领用'),
        ('MAINTAIN', '维修'),
        ('TRANSFER', '转移'),
        ('RETURN', '退库')
    ]
    type_name = models.CharField(max_length=10, choices=type_choices)

    def to_dict(self):
        ''' 转换成字典 '''
        res = super().to_dict()
        res.update({
            'asset': f'{self.asset.name}(id={self.asset.id})',
            'type_name': self.type_name,
            'category': self.asset.category.name,
            'info': '',
        })
        if self.assignee is not None:
            res['info'] = f"维保人：{self.assignee.username}"
        return res


class RequireIssue(AbstractIssue):
    ''' 与资产类型和多个资产相关联的 领用 事项 '''

    asset = models.ManyToManyField(Asset, related_name='被领用资产')
    asset_category = models.ForeignKey(AssetCategory,
                                       on_delete=models.CASCADE,
                                       related_name='领用资产类型')
    reason = models.TextField(verbose_name='申请理由')

    def to_dict(self):
        ''' 转换成字典 '''
        res = super().to_dict()
        res.update({
            'asset': '',
            'type_name': 'REQUIRE',
            'category': self.asset_category.name,
            'info': f'事由：{self.reason}',
        })
        return res
