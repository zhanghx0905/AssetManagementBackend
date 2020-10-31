''' user/test.py '''
import json

from django.test import TestCase

from app.utils import init_test
from .models import User


class UserTest(TestCase):
    ''' Test for user app '''
    login_path = '/api/user/login'

    def setUp(self) -> None:
        ''' 构造时添加一项用户 '''
        init_test(self)

        root = User.objects.get(username='admin').department
        self.department_id = root.id
        user = User(username='zhanghx',
                    department=root)
        user.set_password('zhanghx')
        user.save()

    def test_user_list(self):
        ''' views.user_list '''
        path = '/api/user/list'
        response = self.client.get(path)
        self.assertEqual(response.json()['code'], 200)

    def test_user_exist(self):
        ''' views.user_exist '''
        path = '/api/user/exist'

        response = self.client.get(path)
        self.assertEqual(response.json()['code'], 405)

        response = self.client.post(path)
        self.assertEqual(response.json()['code'], 201)

        response = self.client.post(path,
                                    data=json.dumps({'name': 'admin'}),
                                    content_type='json')
        self.assertTrue(response.json()['exist'])

        response = self.client.post(path,
                                    data=json.dumps({'name': 'noone'}),
                                    content_type='json')
        self.assertFalse(response.json()['exist'])

    def test_user_add_delete(self):
        ''' views.user_add '''
        path = '/api/user/add'

        paras = {
            'name': 'hexiao',
            'department': self.department_id,
            'role': ['IT', 'ASSET']
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)
        self.assertEqual(User.objects.filter(username=paras['name']).count(), 1)

        paras['name'] *= 100
        paras['department'] = -1
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 400)

        path = '/api/user/delete'

        paras['name'] = 'hexiao'
        paras['department'] = self.department_id
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

        paras = {
            'name': 'admin',
            'password': 'admin',
            'department': self.department_id,
            'role': ['IT', 'ASSET', 'SYSTEM']
        }
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 203)

        paras['name'] = 'zhanghx'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)

        paras['password'] = ''
        paras['department'] = -1
        self.client.post(path, data=json.dumps(paras), content_type='json')

    def test_user_lock(self):
        ''' views.user_lock '''
        path = '/api/user/lock'
        paras = {
            'username': 'admin',
            'active': False
        }   # admin 不能锁定
        response = self.client.post(path, data=json.dumps(paras), content_type='json').json()
        self.assertEqual(response['code'], 203)

        # 正常锁定
        paras['username'] = 'zhanghx'
        response = self.client.post(path, data=json.dumps(paras), content_type='json').json()
        self.assertEqual(response['code'], 200)
        response = self.client.post(self.login_path,
                                    data=json.dumps({'username': 'zhanghx', 'password': 'zhanghx'}),
                                    content_type='json')
        self.assertEqual(response.json()['status'], 1)

        # 用户不存在
        paras['username'] = 'nosuchman'
        response = self.client.post(path, data=json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 202)

    def test_user_login_logout(self):
        ''' views.user_login '''
        path = self.login_path

        paras = {
            'username': 'noone',
            'password': 'wrong'
        }   # 测试用户不存在
        response = self.client.post(path, json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['status'], 1)

        paras['username'] = 'zhanghx'
        # 测试密码错误
        response = self.client.post(path, json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['status'], 1)
        # 正常登录在 setUp 中测试，锁定登录在 test_user_lock 中测试

        paras['password'] = 'zhanghx'
        response = self.client.post(path, json.dumps(paras), content_type='json')
        self.client.cookies['Token'] = response.json()['token']

        path = '/api/user/logout'

        response = self.client.post(path, json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['status'], 0)

        # 登出后尝试再登出
        response = self.client.post(path, json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['status'], 1)

    def test_user_info(self):
        ''' views.user_info '''
        path = '/api/user/info'

        response = self.client.post(path).json()
        self.assertFalse(response['status'])
        self.assertEqual(response['userInfo']['name'], 'admin')

    def test_change_password(self):
        ''' test for change_password '''
        path = '/api/user/change-password'

        paras = {
            'oldPassword': 'admin',
            'newPassword': 'admin'
        }
        response = self.client.post(path, json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 200)

        paras['oldPassword'] = 'wrong'
        response = self.client.post(path, json.dumps(paras), content_type='json')
        self.assertEqual(response.json()['code'], 202)

    def test_verify_jwt(self):
        ''' test for utils.user_verified '''
        from datetime import datetime, timedelta

        from jwt import encode

        from .utils import user_verified
        from app.settings import SECRET_KEY

        user_verified({}, [])
        user_verified({'Token': 1}, [])

        username = 'zhanghx'
        token = encode({
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() - timedelta(days=1),   # issued at
            'username': username
        }, SECRET_KEY, algorithm='HS256')
        user_verified({'Token': token}, [])  # Token 过期
        token = encode({
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=1),   # issued at
            'username': username
        }, SECRET_KEY, algorithm='HS256')
        res = user_verified({'Token': token}, [])  # 用户不在线
        self.assertEqual(res, '用户不在线')
