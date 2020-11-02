''' models for issue '''
from django.db import models

from users.models import User
from asset.models import Asset


class IssueConflictError(Exception):
    ''' 同一用户发起的关于同一资产的待办issue只能有一个
    不满足条件则抛出此异常'''


class Issue(models.Model):
    ''' Issue Model '''
    initiator = models.ForeignKey(User, on_delete=models.CASCADE,
                                  verbose_name='发起者',
                                  related_name='initiator')
    handler = models.ForeignKey(User, on_delete=models.CASCADE,
                                verbose_name='处理者',
                                related_name='hanlder')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name='资产')

    # 用于在涉及第三个用户的请求(转移)中记录数据
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

    status_choices = [
        ('DOING', '进行中'),
        ('SUCCESS', '成功'),
        ('FAIL', '失败'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='DOING')

    def to_dict(self):
        ''' 转换成字典 '''
        return {
            'nid': self.id,
            'initiator': self.initiator.username,
            'asset': f'{self.asset.name}(id={self.asset.id})',
            'type_name': self.type_name,
            'assignee': self.assignee.username if self.assignee is not None else '',
            'status': self.status,
        }
