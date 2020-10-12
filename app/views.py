'''
Basic views
'''
# from django.conf import settings

from .utils import gen_response


def get_logs(request):
    ''' api/logs GET
    return: data(str), code =
        200: success
        201: file not found
    '''
    print(request)
    print(request.body)
    print(request.path)
    print(request.method)
    print(request.META.get('REMOTE_ADDR', ''))
    return gen_response(code=200)
