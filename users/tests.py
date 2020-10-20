''' user/test.py '''
import json

from django.test import TestCase

from .apps import add_admin
from .models import User


class UserTest(TestCase):
    ''' Test for user app '''

    def setUp(self) -> None:
        ''' 构造时添加一项 '''
        user = User(username='zhanghx',
                    department='thu')
        user.set_password('zhanghx')
        user.save()

    def illegal_input(self, path: str):
        ''' 对于只接受POST方法的api 测试不合法的输入 '''
        response = self.client.get(path)
        self.assertEqual(response.json()['code'], 405)

        response = self.client.post(path)
        self.assertEqual(response.json()['code'], 201)

    def admin_login(self):
        ''' 登录管理员用户 '''
        add_admin()
        path = '/api/user/login'
        paras = {'username': 'admin', 'password': 'admin'}
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.client.cookies['Token'] = response.json()['token']

    def test_user_list(self):
        ''' views.user_list '''
        path = '/api/user/list'

        self.admin_login()

        response = self.client.post(path)
        self.assertEqual(response.json()['code'], 405)

        response = self.client.get(path)
        self.assertEqual(response.json()['code'], 200)

    def test_user_exist(self):
        ''' views.user_exist '''
        path = '/api/user/exist'

        self.admin_login()

        self.illegal_input(path)

        response = self.client.post(path, data=json.dumps({'name': 'admin'}), content_type='json')
        self.assertTrue(response.json()['exist'])

        response = self.client.post(path, data=json.dumps({'name': 'nothisman'}), content_type='json')
        self.assertFalse(response.json()['exist'])

    def test_user_add_delete(self):
        ''' views.user_add '''
        path = '/api/user/add'
        self.admin_login()
        self.illegal_input(path)

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

        path = '/api/user/delete'

        self.illegal_input(path)

        paras['name'] = 'hexiao'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)
        self.assertEqual(User.objects.filter(username=paras['name']).count(), 0)

        paras['name'] = 'nosuchman'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 202)

        paras['name'] = 'admin'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 203)

    def test_user_edit(self):
        ''' views.user_edit '''
        path = '/api/user/edit'

        self.admin_login()
        self.illegal_input(path)

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
        self.admin_login()

        self.illegal_input(path)

        paras = {
            'username': 'admin',
            'active': False
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 203)

        paras['username'] = 'zhanghx'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)
        response = self.client.post('/api/user/login',
                                    data=json.dumps({'username': 'zhanghx', 'password': 'zhanghx'}),
                                    content_type='json')
        self.assertEqual(response.json()['status'], 1)

        paras['username'] = 'nosuchman'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 202)

    def test_user_login_logout(self):
        ''' views.user_login '''

    def test_user_info(self):
        ''' views.user_info '''
