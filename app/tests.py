''' app/tests.py '''
import json

from django.test import TestCase

from app.utils import gen_response, parse_args


class AppTests(TestCase):
    ''' Test cases for project app '''

    def test_get_logs(self):
        ''' views.get_logs '''

        # 测试http method error
        path = "/api/logs"
        response = self.client.get(path)
        self.assertEqual(response.json()['code'], 405)

        # 测试 size
        response = self.client.post(
            path, json.dumps({'size': 1}), content_type='json')
        self.assertEqual(response.json()['code'], 200)
        logs = response.json()['data']
        self.assertEqual(len(logs), 1)

        # 测试 offset, size
        response = self.client.post(path, json.dumps(
            {'offset': 1, 'size': 1}), content_type='json')
        self.assertEqual(response.json()['code'], 200)
        logs = response.json()['data']
        self.assertEqual(len(logs), 1)

    def test_parse_args(self):
        ''' utils.parse_args '''
        res = parse_args(json.dumps({'name': 'zhang'}), 'name')
        self.assertEqual(res[0], 'zhang')

        res = parse_args('', 'name', name='zhang')
        self.assertEqual(res[0], 'zhang')

        with self.assertRaises(KeyError):
            parse_args('', 'name')

    def test_gen_response(self):
        ''' utils.gen_response '''
        response = gen_response(name='zhang')
        response_para = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response_para['name'], 'zhang')

    def test_wsgi(self):
        ''' wsgi '''
        from . import wsgi
        self.assertEqual(wsgi.__name__, 'app.wsgi')
