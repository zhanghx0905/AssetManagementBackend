''' user/test.py '''
import json

from django.test import TestCase

from .apps import add_admin
from .models import User


class UserTest(TestCase):
    ''' Test for user app '''
    token = None

    def test_user_model(self):
        ''' models.User '''
        add_admin()
        admin = User.objects.get(username='admin')
        self.assertEqual(admin.__str__(), 'admin')
        self.token = admin.generate_jwt_token()

    def test_user_add(self):
        ''' views.user_add '''
        path = '/api/user/add'

        illegal_input(self, path)

        paras = {
            'name': 'hexiao',
            'password': 'zhanghx',
            'department': 'thu',
            'role': ['IT', 'ASSET']
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)
        self.assertEqual(User.objects.filter(username=paras['name']).count(), 1)

        paras['name'] *= 10
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 400)

    def test_user_exist(self):
        ''' views.user_exist '''
        path = '/api/user/exist'

        illegal_input(self, path)
        add_admin()
        response = self.client.post(path, data=json.dumps({'name': 'admin'}), content_type='json')
        self.assertTrue(response.json()['exist'])

    def test_user_list(self):
        ''' views.user_list '''
        path = '/api/user/list'

        response = self.client.post(path)
        self.assertEqual(response.json()['code'], 405)

        add_admin()
        response = self.client.get(path)
        self.assertEqual(response.json()['code'], 200)
        users_list = response.json()['data']
        self.assertEqual(len(users_list), 1)
        self.assertEqual(users_list[0]['name'], 'admin')

    def test_user_edit(self):
        ''' views.user_edit '''
        path = '/api/user/edit'
        illegal_input(self, path)

        add_admin()
        paras = {
            'name': 'admin',
            'password': 'admin',
            'department': 'thu',
            'role': ['IT', 'ASSET', 'SYSTEM']
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)
        admin = User.objects.get(username='admin')
        self.assertEqual(admin.department, paras['department'])

        paras['name'] = 'nothisman'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 202)

    def test_user_lock(self):
        ''' views.user_lock '''
        path = '/api/user/lock'
        illegal_input(self, path)

        add_admin()
        paras = {
            'username': 'admin',
            'active': False
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 203)

        paras['username'] = 'zhanghx'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 202)

    def test_user_login_logout(self):
        ''' views.user_login '''

    def test_user_info(self):
        ''' views.user_info '''


def illegal_input(self: UserTest, path: str):
    ''' 对于只接受POST方法的api 测试不合法的输入 '''
    response = self.client.get(path)
    self.assertEqual(response.json()['code'], 405)

    response = self.client.post(path)
    self.assertEqual(response.json()['code'], 201)
