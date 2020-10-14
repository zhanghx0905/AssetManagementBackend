'''
Basic views
'''
from .settings import LOGS_FILE_DIR
from .utils import gen_response


def get_logs(request):
    ''' api/logs GET
    para: offset(int) = 0, size(int) = 20
    return: data(str), code =
        200: success
    '''
    if request.method == 'GET':
        offset = int(request.GET.get('offset', 0))
        size = int(request.GET.get('size', 20))

        data = []
        with open(LOGS_FILE_DIR, 'r', encoding='utf8') as logs_file:
            logs = logs_file.readlines()[::-1]
            data = logs[offset:offset + size]

        return gen_response(code=200, data=''.join(data))
    return gen_response(code=405, message=f'method {request.method} not allowed')
