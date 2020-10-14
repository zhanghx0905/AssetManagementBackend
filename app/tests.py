''' app/tests.py '''
import json

from django.test import TestCase

from app.utils import gen_response, parse_args


class AppTests(TestCase):
    ''' Test cases for project app '''

    def test_get_logs(self):
        ''' views.get_logs '''

        def get_logs_len(logs):
            ''' get length of logs '''
            return len(logs.split('\n')[:-1])

        # 测试http method error
        path = "/api/logs"
        response = self.client.post(path)
        self.assertEqual(response.json()['code'], 405)

        # 测试 size
        response = self.client.get(path, {'size': 1})
        self.assertEqual(response.json()['code'], 200)
        logs = response.json()['data']
        self.assertEqual(get_logs_len(logs), 1)

        # 测试 offset, size
        response = self.client.get(path, {'offset': 1, 'size': 1})
        self.assertEqual(response.json()['code'], 200)
        logs = response.json()['data']
        self.assertEqual(get_logs_len(logs), 1)

    def test_parse_args(self):
        ''' utils.parse_args '''
        valid, res = parse_args(json.dumps({'name': 'zhang'}), 'name')
        self.assertTrue(valid)
        self.assertEqual(res[0], 'zhang')

        valid, res = parse_args('', 'name', name='zhang')
        self.assertTrue(valid)
        self.assertEqual(res[0], 'zhang')

        valid = parse_args('', 'name')[0]
        self.assertFalse(valid)

    def test_gen_response(self):
        ''' utils.gen_response '''
        response = gen_response(name='zhang')
        response_para = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response_para['name'], 'zhang')
