''' app/tests.py '''
import json

from django.test import TestCase

from app.utils import init_test, parse_list


class AppTests(TestCase):
    ''' Test cases for project app '''

    def setUp(self) -> None:
        ''' 添加并登录admin '''
        init_test(self)

    def test_get_logs(self):
        ''' views.get_logs '''

        # 测试http method error
        path = "/api/logs"

        # 测试 size
        response = self.client.post(
            path, json.dumps({'size': 1}), content_type='json')
        self.assertEqual(response.json()['code'], 200)

        # 测试 offset, size
        response = self.client.post(path, json.dumps(
            {'offset': 1, 'size': 1}), content_type='json')
        self.assertEqual(response.json()['code'], 200)

    def test_wsgi(self):
        ''' wsgi '''
        from . import wsgi
        self.assertEqual(wsgi.__name__, 'app.wsgi')

    def test_parse_list(self):
        ''' 测试parse_list '''
        parse_list('test')
        with self.assertRaises(KeyError):
            parse_list(json.dumps({'data': [{'val': 1}]}), 'name')
