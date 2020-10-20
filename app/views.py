'''
Basic views
'''
import json

from .settings import LOGS_FILE_DIR
from .utils import gen_response, parse_args


def get_logs(request):
    ''' api/logs GET
    para: offset(int) = 0, size(int) = 20
    return: data(str), code =
        200: success
    '''
    if request.method == 'POST':
        _, res = parse_args(request.body, 'offset', 'size', offset=0, size=20)
        offset, size = res

        data = []
        with open(LOGS_FILE_DIR, 'r', encoding='utf8') as logs_file:
            logs = logs_file.readlines()[::-1]
            data = logs[offset: (offset + size)]
        data = [json.loads(line[:-1]) for line in data]
        return gen_response(code=200, data=data, message='获取日志')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
