''' test of model department'''
import json

from django.test import TestCase

from app.utils import init_test
from .models import Department


class DepartmentTest(TestCase):
    ''' test for App department '''

    def setUp(self) -> None:
        ''' add admin and login
        在顶层部门下添加一个子部门 '''
        init_test(self)
        Department.objects.create(name='子部门', parent=Department.root())

    def test_tree(self):
        ''' test for department/tree '''
        response = self.client.get(path='/api/department/tree')
        self.assertEqual(response.json()['code'], 200)

    def test_add_and_delete(self):
        ''' test for department/add '''
        path = '/api/department/add'
        paras = {
            'parent_id': 1,
            'name': '子部门'
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)

        path = '/api/department/delete'
        paras = {
            'id': 2
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)

        paras['id'] = 1
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 203)

    def test_edit(self):
        '''  test for department/edit '''
        path = '/api/department/edit'
        paras = {
            'id': 1,
            'name': '新部门'
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)
