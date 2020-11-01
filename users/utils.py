''' utils for App users '''
from functools import partial, wraps

import jwt

from app.settings import SECRET_KEY
from app.utils import gen_response
from .models import User


def user_verified(cookies, perms) -> str:
    '''
    验证 token 是否合法，
    与装饰器分离以便测试
    '''
    try:
        token = cookies['Token']
    except KeyError:
        return 'Token 未给出'
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return 'Token 已过期'
    except jwt.InvalidTokenError:
        return 'Token 不合法'

    user: User = User.objects.get(username=decoded['username'])
    if user.token != token:
        return '用户不在线'
    if not user.has_perms(perms):
        return '权限不足'
    return 'OK'


def auth_permission_required(*perms):
    '''
    用于用户验证的装饰器
    该装饰器会验证 cookies 里的 token 是否合法，
    错误时返回 status=1, code=401

    例:
    @catch_exception('POST')
    @auth_permission_required("users.IT", "users.SYSTEM")
    def foo(request):
        pass
    '''
    error_response = partial(gen_response, status=1, code=401)

    def decorator(view_func):
        ''' 多嵌套一层，为了给装饰器传参 '''
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            ''' 装饰器内函数 '''
            verified = user_verified(request.COOKIES, perms)
            if verified != 'OK':
                return error_response(message=verified)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
