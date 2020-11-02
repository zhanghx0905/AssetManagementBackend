'''test for app asset'''
from django.test import TestCase

from app.utils import init_test
from users.apps import add_old_asset
from .apps import init_category


class AssetTest(TestCase):
    ''' Testcases for app asset '''

    def setUp(self) -> None:
        ''' 加入admin并登录，初始化资产类型
        添加一个旧资产 '''
        init_test(self)
        init_category()
        add_old_asset()

    def test_category_tree(self):
        ''' test for category_tree '''
        response = self.client.get('/api/asset/category/tree')
        self.assertEqual(response.json()['code'], 200)
