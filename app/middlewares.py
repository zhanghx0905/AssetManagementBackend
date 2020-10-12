''' app/middlewares.py '''
import json
import logging
import threading

from django.utils.deprecation import MiddlewareMixin

LOCAL = threading.local()


class RequestLogFilter(logging.Filter):
    '''
    日志过滤器
    '''

    def filter(self, record):
        record.body = getattr(LOCAL, 'body', 'none')
        record.path = getattr(LOCAL, 'path', 'none')
        record.method = getattr(LOCAL, 'method', 'none')
        record.status_code = getattr(LOCAL, 'status_code', 'none')

        return True


class RequestLogMiddleware(MiddlewareMixin):
    '''
    将request的信息记录在当前的请求线程上。
    '''

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.api_logger = logging.getLogger('web.log')

    def __call__(self, request):

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            body = dict()

        if request.method == 'GET':
            body.update(dict(request.GET))
        else:
            body.update(dict(request.POST))

        LOCAL.body = body
        LOCAL.path = request.path
        LOCAL.method = request.method

        response = self.get_response(request)

        LOCAL.status_code = response.status_code
        self.api_logger.info('Http called')

        return response
