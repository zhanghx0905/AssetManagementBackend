'''test for app asset'''
import json

from django.test import TransactionTestCase

from app.utils import init_test
from asset.models import AssetCategory
from users.apps import add_old_asset
from .apps import init_category


class AssetTest(TransactionTestCase):
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

    def test_category(self):
        ''' test for category_add category_delete category_edit '''
        # 增加一类
        path = '/api/asset/category/add'
        paras = {"parent_id": 1, "name": "me"}
        response = self.client.post(path,
                                    json.dumps(paras),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        response = self.client.post(path,
                                    json.dumps(paras),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 203)

        # 修改类名
        path = '/api/asset/category/edit'
        paras = {"id": 2, "name": "new"}
        response = self.client.post(path,
                                    json.dumps(paras),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        paras['name'] = AssetCategory.root().name
        response = self.client.post(path,
                                    json.dumps(paras),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 203)

        # 删除类
        path = '/api/asset/category/delete'
        response = self.client.post(path,
                                    json.dumps({"id": 2}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        response = self.client.post(path,
                                    json.dumps({"id": 1}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 203)
