'''
Basic views
'''
from .settings import LOGS_FILE_DIR
from .utils import gen_response, parse_args


def get_logs(request):
    ''' api/logs GET
    para: offset(int) = 0, size(int) = 20
    return: data(str), code =
        200: success
    '''
    if request.method == 'GET':
        valid, res = parse_args(request.body, 'offset', 'size', offset=0, size=20)
        offset, size = res if valid else (0, 20)
        data = []
        with open(LOGS_FILE_DIR, 'r') as logs:
            data = logs.readlines()[-1-offset - size:-1-offset]
        return gen_response(code=200, data='\n'.join(data))
    return gen_response(code=405, message=f'method {request.method} not allowed')
