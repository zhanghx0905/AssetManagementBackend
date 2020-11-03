'''test for app asset'''
import json

from django.test import TestCase
from django.db import transaction
from simple_history.utils import update_change_reason

from app.utils import init_test
from asset.models import AssetCategory, Asset
from users.apps import add_old_asset


class AssetTest(TestCase):
    ''' Testcases for app asset
    要触发 IntegrityError，必须在 transaction.atomic() 上下文中
    '''

    def setUp(self) -> None:
        ''' 加入admin并登录，初始化资产类型
        添加一个旧资产 '''
        init_test(self)
        root = AssetCategory(name='资产', parent=None)
        root.save()
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
        with transaction.atomic():
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
        with transaction.atomic():
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
        with transaction.atomic():
            response = self.client.post(path,
                                        json.dumps({"id": 1}),
                                        content_type='json')
        self.assertEqual(response.json()['code'], 203)

    def test_custom_attr(self):
        ''' 测试自定义属性的添加和获取 '''
        path = '/api/asset/custom/edit'
        # 添加同名属性
        with transaction.atomic():
            response = self.client.post(path,
                                        json.dumps({'custom': ['a', 'a']}),
                                        content_type='json')
        self.assertEqual(response.json()['code'], 203)

        response = self.client.post(path,
                                    json.dumps({'custom': ['流水线']}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        response = self.client.get('/api/asset/custom/list').json()
        self.assertEqual(response['code'], 200)
        self.assertListEqual(response['data'], ['流水线'])

    def test_asset_available(self):
        ''' 测试获取可领用资产列表 asset/avaliable '''
        response = self.client.get('/api/asset/available').json()
        self.assertEqual(response['code'], 200)
        self.assertEqual(len(response['data']), 1)

    def test_asset_history(self):
        ''' 测试获取资产历史 asset/history '''
        asset: Asset = Asset.objects.get(id=1)  # 旧资产
        asset.description = '修改信息'
        asset.save()
        update_change_reason(asset, '修改')

        response = self.client.post('/api/asset/history',
                                    json.dumps({'nid': 1}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

    def test_asset_retire_list(self):
        ''' 测试资产清退和部门资产列表 '''
        path = '/api/asset/retire'
        response = self.client.post(path,
                                    json.dumps({'nid': 1}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        response = self.client.post(path,
                                    json.dumps({'nid': 1}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 203)

        response = self.client.get('/api/asset/list').json()
        self.assertEqual(response['code'], 200)
        self.assertEqual(len(response['data']), 1)

    def test_asset_query(self):
        ''' 测试资产搜索 '''
        path = '/api/asset/query'
        paras = {
            'name': '旧',
            'category': '资产',
            'description': '信息'
        }
        response = self.client.post(path,
                                    json.dumps(paras),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)
