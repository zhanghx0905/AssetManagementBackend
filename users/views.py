''' user/view.py, all in domain api/user/ '''
from functools import partial

import jwt

from app.settings import DEFAULT_PASSWORD, SECRET_KEY
from app.utils import catch_exception, gen_response, parse_args
from department.models import Department
from .models import User


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
        def _wrapped_view(request, *args, **kwargs):
            ''' 装饰器内函数 '''
            try:
                token = request.COOKIES['Token']
            except KeyError:
                return error_response(message='Token 未给出')
            try:
                decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                username = decoded['username']
            except jwt.ExpiredSignatureError:
                return error_response(message='Token 已过期')
            except jwt.InvalidTokenError:
                return error_response(message='Token 不合法')

            user: User = User.objects.get(username=username)
            if user.token != token:
                return error_response(message='用户不在线')
            if not user.active:
                return error_response(message='用户未激活')

            if not user.has_perms(perms):
                return error_response(message='用户权限不足')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


@catch_exception('GET')
@auth_permission_required('users.SYSTEM')
def user_list(request):
    ''' api/user/list GET
    返回所有用户的列表。
    return: data([{}]), code =
        200: success
    '''
    all_users = User.objects.filter()
    res = [{
        'name': user.username,
        'department': user.department.name,
        'department_id': user.department.id,
        'role': user.gen_roles(),
        'is_active': user.active,
    } for user in all_users]
    return gen_response(code=200, data=res, message='获取用户列表')


@catch_exception('POST')
@auth_permission_required('users.SYSTEM')
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
    name = parse_args(request.body, 'name')[0]
    if name == 'admin':
        return gen_response(message='admin 不能被删除', code=203)
    user = User.objects.get(username=name)
    user.delete()
    return gen_response(code=200, message=f'删除用户 {name}')


@catch_exception('POST')
@auth_permission_required('users.SYSTEM')
def user_exist(request):
    ''' api/user/exist POST
    用户名是否存在。
    para: name(str)
    return: exist(bool), code =
        200: success
        201: parameter error
    '''
    name = parse_args(request.body, 'name')[0]

    exist = User.objects.filter(username=name).exists()
    return gen_response(code=200, exist=exist)


@catch_exception('POST')
@auth_permission_required('users.SYSTEM')
def user_add(request):
    '''  api/user/add POST
    添加用户。
    para: name(str), department(str), role([...])
    return: code =
        200: success
        201: parameter error
        400: Validation Error when saving user
    '''

    name, department_id, roles = parse_args(request.body,
                                            'name', 'department', 'role',
                                            department='')
    try:
        department = Department.objects.get(id=department_id)
    except Department.DoesNotExist:
        department = Department.root()

    user = User(username=name,
                department=department)
    user.set_password(DEFAULT_PASSWORD)
    user.full_clean()
    user.save()
    user.set_roles(roles)
    return gen_response(code=200, message=f'添加用户 {name}')


@catch_exception('POST')
@auth_permission_required('users.SYSTEM')
def user_edit(request):
    '''  api/user/edit POST
    编辑用户。
    para: name(str), password(str), department_id(str), role([...])
    return: code =
        200: success
        201: parameter error
        202：no such user
    '''
    name, pwd, department_id, roles = parse_args(request.body,
                                                 'name', 'password', 'department', 'role',
                                                 department='')

    if name == 'admin':
        return gen_response(code=203, message="admin 的信息不能被修改")

    user = User.objects.get(username=name)
    if pwd != '':
        user.set_password(pwd)
    try:
        department = Department.objects.get(id=department_id)
    except Department.DoesNotExist:
        department = Department.root()
    user.department = department
    user.save()
    user.set_roles(roles)

    return gen_response(code=200, message=f'{user.username} 信息修改')


@catch_exception('POST')
@auth_permission_required('users.SYSTEM')
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
    username, active = parse_args(request.body, 'username', 'active')

    if username == 'admin':
        return gen_response(message='admin 必须处于活跃状态', code=203)
    user = User.objects.get(username=username)
    user.active = active
    user.save()
    return gen_response(code=200)


@catch_exception('POST')
def user_login(request):
    '''  api/user/login POST
    用户登录。
    para: username(str), password(str)
    return: code =
        201: parameter error
            status =
        0: success
        1: fall
    '''

    name, pwd = parse_args(request.body, 'username', 'password')
    user = User.objects.get(username=name)

    if not user.check_password(pwd):
        return gen_response(message='密码有误', status=1)
    if not user.active:
        return gen_response(message='用户不处于活跃状态', status=1)

    user.token = user.generate_jwt_token()
    user.save()

    return gen_response(token=user.token, status=0, message=f'{name} 登录')


@catch_exception('POST')
@auth_permission_required()
def user_logout(request):
    '''  api/user/login POST
    用户登出。
    return: status =
        0: success
        1: fall
    '''
    user = request.user
    user.token = ''
    user.save()

    return gen_response(status=0, message=f'{user.username} 登出')


@catch_exception('POST')
@auth_permission_required()
def user_info(request):
    '''  api/user/info POST
    用户信息。
    return: userInfo = {name(str), role([]), avatar('')}
        status =
        0: success
        1: fall
    '''
    user = request.user
    info = {
        "name": user.username,
        "role": user.gen_roles(),
        "avatar": ''
    }
    return gen_response(status=0, userInfo=info, message=f'获取用户 {user.username} 信息')


@catch_exception('POST')
@auth_permission_required()
def user_change_password(request):
    ''' api/user/change-password POST
    更改自己的密码。
    para: oldPassword(str), newPassword(str)
    '''
    user = request.user
    old_pwd, new_pwd = parse_args(request.body, 'oldPassword', 'newPassword')

    if not user.check_password(old_pwd):
        return gen_response(message='旧密码错误', code=202)
    user.set_password(new_pwd)
    user.save()
    return gen_response(code=200, message=f'用户 {user.username} 密码更改')
