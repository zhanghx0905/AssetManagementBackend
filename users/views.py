''' user/view.py, all in domain api/user/ '''

import logging

import jwt
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError

from app.settings import SECRET_KEY
from app.utils import gen_response, parse_args
from .models import User

LOGGER = logging.getLogger('web.log')


def auth_permission_required(view_func):
    ''' 用于用户验证的装饰器
    该装饰器会验证 cookies 里的 token 是否合法，
    并将对应用户以参数 user 传给被装饰函数
    错误时返回 status=1, code=401
    '''
    def _wrapped_view(request, *args, **kwargs):
        ''' 装饰器内函数 '''
        token = request.COOKIES['Token']
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            username = decoded['username']
        except jwt.ExpiredSignatureError:
            return gen_response(status=1, message='Token expired', code=401)
        except jwt.InvalidTokenError:
            return gen_response(status=1, message='Invalid token', code=401)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return gen_response(status=1, message='no such user', code=401)

        if user.token != token:
            return gen_response(status=1, message='user not online', code=401)
        if not user.is_active:
            return gen_response(status=1, message='user is not activated', code=401)
        return view_func(request, user=user, *args, **kwargs)
    return _wrapped_view


def gen_roles(user: User) -> list:
    ''' generate roles to deliver for a user '''
    role = []
    if user.is_it_manager:
        role.append('IT')
    if user.is_asset_manager:
        role.append('ASSET')
    if user.is_system_manager:
        role.append('SYSTEM')
    role.append('STAFF')
    return role


def user_list(request):
    ''' api/user/list GET
    返回所有用户的列表。
    return: data([{}]), code =
        200: success
    '''
    if request.method == 'GET':
        all_users = User.objects.filter()
        res = []
        for user in all_users:
            res.append({'name': user.username,
                        'department': user.department,
                        'role': gen_roles(user),
                        'is_active': user.is_active,
                        })

        return gen_response(code=200, data=res)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_delete(request):
    ''' api/user/delete POST
    删除用户。
    para: name(str)
    return: code =
        200: success
        201: parameter error
        202: no such named user
        203: admin can't be deleted
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name')
        if not valid:
            return gen_response(code=201, message=res)
        name = res[0]

        if name == 'admin':
            return gen_response(message='admin can not be deleted', code=203)
        user = User.objects.get(username=name)
        if not user:
            return gen_response(message='no such user', code=202)
        user.delete()
        return gen_response(code=200)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_exist(request):
    ''' api/user/exist POST
    用户名是否存在。
    para: name(str)
    return: exist(bool), code =
        200: success
        201: parameter error
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name')
        if not valid:
            return gen_response(code=201, message=res)
        name = res[0]

        cnt = User.objects.filter(username=name).count()
        return gen_response(code=200, exist=(cnt == 1))
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_add(request):
    '''  api/user/add POST
    添加用户。
    para: name(str), password(str), department(str), role([...])
    return: code =
        200: success
        201: parameter error
        400: Validation Error when saving user
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name', 'password', 'department', 'role')
        if not valid:
            return gen_response(code=201, message=res)
        name, pwd, department, roles = res
        is_it_manager = 'IT' in roles
        is_asset_manager = 'ASSET' in roles
        is_system_manager = 'SYSTEM' in roles

        pwd = make_password(pwd, None)

        user = User(username=name,
                    password=pwd,
                    department=department,
                    is_it_manager=is_it_manager,
                    is_asset_manager=is_asset_manager,
                    is_system_manager=is_system_manager)
        try:
            user.full_clean()
            user.save()
        except ValidationError as error:
            return gen_response(message=f"Validation Error of user, {error}", code=400)
        return gen_response(code=200)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_edit(request):
    '''  api/user/edit POST
    编辑用户。
    para: name(str), password(str), department(str), role([...])
    return: code =
        200: success
        201: parameter error
        202：no such user
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name', 'password', 'department', 'role')
        if not valid:
            return gen_response(code=201, message=res)
        name, pwd, department, roles = res
        user = User.objects.filter(username=name)
        if not user:
            return gen_response(message='no such user', code=202)

        is_it_manager = 'IT' in roles
        is_asset_manager = 'ASSET' in roles
        is_system_manager = 'SYSTEM' in roles

        pwd = make_password(pwd, None)

        user.update(password=pwd,
                    department=department,
                    is_it_manager=is_it_manager,
                    is_asset_manager=is_asset_manager,
                    is_system_manager=is_system_manager)
        return gen_response(code=200)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_lock(request):
    ''' api/user/lock POST
    锁定用户
    para: username(str), active(0/1)
    return: code =
        200: success
        201: parameter error
        202：no such user
        203: admin can not be locked
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'username', 'active')
        if not valid:
            return gen_response(code=201, message=res)
        username, active = res
        if username == 'admin':
            return gen_response(message='admin can not be locked', code=203)
        user = User.objects.filter(username=username)
        if not user:
            return gen_response(message='no such user', code=202)

        user.update(is_active=active)
        return gen_response(code=200)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_login(request):
    '''  api/user/login POST
    用户登录。
    para: name(str), password(str)
    return: code =
        201: parameter error
        status =
        0: success
        1: fall
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'username', 'password')
        if not valid:
            return gen_response(code=201, message=res)
        name, pwd = res
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            return gen_response(message='nonexistent users', status=1)

        if not check_password(pwd, user.password):
            return gen_response(message='invalid password', status=1)
        if not user.is_active:
            return gen_response(message='user is locked', status=1)

        user.token = user.generate_jwt_token()
        user.save()

        LOGGER.debug('%s login', name)
        return gen_response(token=user.token, status=0)
    return gen_response(code=405, message=f'method {request.method} not allowed')


@auth_permission_required
def user_logout(request, user):
    '''  api/user/login POST
    用户登出。
    return: status =
        0: success
        1: fall
    '''
    if request.method == 'POST':
        user.token = ''
        user.save()

        LOGGER.debug('%s login', user.username)
        return gen_response(status=0)
    return gen_response(code=405, message=f'method {request.method} not allowed')


@auth_permission_required
def user_info(request, user):
    '''  api/user/login POST
    用户信息。
    return: userInfo = {name(str), role([]), avatar('')}
        status =
        0: success
        1: fall
    '''
    if request.method == 'POST':
        info = {
            "name": user.username,
            "role": gen_roles(user),
            "avatar": ''
        }
        return gen_response(status=0, userInfo=info)
    return gen_response(code=405, message=f'method {request.method} not allowed')
