''' models for issue '''
from django.db import models

from users.models import User
from asset.models import Asset


class AbstractIssue(models.Model):
    ''' Issue 基类 用于复用字段 '''
    initiator = models.ForeignKey(User, on_delete=models.CASCADE,
                                  verbose_name='发起者',
                                  related_name='initiator')
    handler = models.ForeignKey(User, on_delete=models.CASCADE,
                                verbose_name='处理者',
                                related_name='hanlder')

    # 用于在涉及第三个用户的请求(转移)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE,
                                 verbose_name='被分配者',
                                 related_name='assignee',
                                 blank=True, null=True)

    status_choices = [
        ('DOING', '进行中'),
        ('SUCCESS', '成功'),
        ('FAIL', '失败'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='DOING')

    def to_dict(self):
        ''' 用于复用实现 '''
        return {
            'nid': self.id,
            'initiator': self.initiator.username,
            'assignee': self.assignee.username if self.assignee is not None else '',
            'status': self.status,
        }

    class Meta:
        abstract = True


class Issue(AbstractIssue):
    ''' Issue 数据类
    用于与单个资产关联的事项，包括维修，转移，退库 '''

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name='资产')

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
        })
        return res
