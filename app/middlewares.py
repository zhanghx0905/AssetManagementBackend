''' app/middlewares.py '''
import logging
import threading

import jwt
from django.utils.deprecation import MiddlewareMixin

LOCAL = threading.local()
DummyBase = logging.Filter


class RequestLogFilter(DummyBase):
    '''
    日志过滤器
    '''

    def filter(self, record):
        record.path = getattr(LOCAL, 'path', 'none')
        record.method = getattr(LOCAL, 'method', 'none')
        record.username = getattr(LOCAL, 'username', 'none')

        return True


class RequestLogMiddleware(MiddlewareMixin):
    '''
    将request的信息记录在当前的请求线程上。
    '''

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.api_logger = logging.getLogger('web.log')

    def __call__(self, request):

        LOCAL.path = request.path
        LOCAL.method = request.method
        from user.models import User
        try:
            token = request.COOKIES['Token']
            decoded = jwt.decode(token, verify=False)
            LOCAL.username = decoded['username']
            request.user = User.objects.get(username=decoded['username'])
        except (KeyError, jwt.PyJWTError, User.DoesNotExist):
            pass

        response = self.get_response(request)

        return response
