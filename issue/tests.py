''' TestCase for issue '''
import json

from django.test import TestCase

from app.utils import init_test
from asset.apps import init_category
from asset.models import Asset, AssetCategory
from users.models import User
from .models import Issue


class IssueTest(TestCase):
    ''' test for Issue '''

    handle_url = '/api/issue/handle'

    def setUp(self) -> None:
        ''' 创建一个admin名下的资产 '''
        init_test(self)
        init_category()
        Asset.objects.create(name='资产',
                             quantity=1, value=1,
                             category=AssetCategory.root(),
                             type_name='ITEM', status='IDLE',
                             service_life=10,
                             owner=User.admin())

    def test_require_return_handle(self):
        ''' test for issue_require issue_return '''
        # require
        response = self.client.post('/api/issue/require',
                                    json.dumps({"nid": 1}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        # 触发 IssueConflictIssue 异常
        response = self.client.post('/api/issue/require',
                                    json.dumps({"nid": 1}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 203)

        # handle
        response = self.client.post(self.handle_url,
                                    json.dumps({"nid": 1, "success": True}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        response = self.client.post(self.handle_url,
                                    json.dumps({"nid": 1, "success": False}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        status = Asset.objects.get(id=1).status
        self.assertEqual(status, "IN_USE")

        # return
        response = self.client.post('/api/issue/return',
                                    json.dumps({"nid": 1}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        # handle
        response = self.client.post(self.handle_url,
                                    json.dumps({"nid": 2, "success": True}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        status = Asset.objects.get(id=1).status
        self.assertEqual(status, "IDLE")

    def test_fix_handle(self):
        ''' test for issue_fix '''
        response = self.client.post('/api/issue/fix',
                                    json.dumps({"nid": 1, "username": "admin"}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        response = self.client.post('/api/issue/fix',
                                    json.dumps({"nid": 1, "username": "admin"}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 203)

        status = Asset.objects.get(id=1).status
        self.assertEqual(status, "IN_MAINTAIN")

        response = self.client.post(self.handle_url,
                                    json.dumps({"nid": 1, "success": True}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

    def test_transfer_handle(self):
        ''' test for issue_transfer and delete'''
        response = self.client.post('/api/issue/transfer',
                                    json.dumps({"nid": 1, "username": "admin"}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

        response = self.client.post('/api/issue/transfer',
                                    json.dumps({"nid": 1, "username": "admin"}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 203)

        response = self.client.post(self.handle_url,
                                    json.dumps({"nid": 1, "success": True}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)

    def test_list_delete(self):
        ''' test for handling_list and waiting_list
        issue_delete '''
        asset = Asset.objects.get(id=1)
        Issue.objects.create(initiator=User.admin(), handler=User.admin(),
                             asset=asset, type_name='REQUIRE', status='DOING')

        response = self.client.get('/api/issue/handling').json()
        self.assertEqual(response['code'], 200)
        self.assertEqual(len(response['data']), 1)

        response = self.client.get('/api/issue/waiting').json()
        self.assertEqual(response['code'], 200)
        self.assertEqual(len(response['data']), 1)

        # delete
        response = self.client.post('/api/issue/delete',
                                    json.dumps({"nid": 1}),
                                    content_type='json')
        self.assertEqual(response.json()['code'], 200)
        self.assertFalse(Issue.objects.filter().exists())
