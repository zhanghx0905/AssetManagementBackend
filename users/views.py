''' user/view.py, all in domain api/user/ '''
import json

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse

from .models import User


# token(str): user(User)
CUR_USERS = {}


def gen_response(**data):
    ''' gerenate json response, at response.data '''
    return JsonResponse(data)


def parse_args(dic: str, *args):
    ''' parse para from json str '''
    dic = json.loads(dic)
    res = []
    for arg in args:
        val = dic.get(arg, None)
        if val is None:
            return (False, f"{arg} is not given")
        res.append(val)
    return (True, res)


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
        all_users = User.objects.all()
        res = []
        for user in all_users:
            res.append({'name': user.username,
                        'password': user.password,
                        'department': user.department,
                        'role': gen_roles(user)
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
        user = User.objects.filter(username=name)
        if not user:
            return gen_response(message='no such user', code=202)
        user[0].delete()
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
    return: exist(bool), code =
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

        user = User.objects.filter(username=name)
        if not user:
            return gen_response(message='nonexistent users', status=1)
        user = user[0]
        if not check_password(pwd, user.password):
            return gen_response(message='invalid password', status=1)
        global CUR_USERS
        token = make_password(name)
        CUR_USERS[token] = user
        return gen_response(token=token, status=0)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_logout(request):
    '''  api/user/login POST
    用户登出。
    return: status =
        0: success
        1: fall
    '''
    if request.method == 'POST':
        token = request.COOKIES['Token']
        user = CUR_USERS.get(token, None)
        if user is None:
            return gen_response(message="User not online", status=1)
        CUR_USERS.pop(token)
        return gen_response(status=0)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_info(request):
    '''  api/user/login POST
    用户信息。
    return: userInfo = {name(str), role([]), avatar('')}
        status =
        0: success
        1: fall
    '''
    if request.method == 'POST':
        token = request.COOKIES['Token']
        user = CUR_USERS.get(token, None)
        if user is None:
            return gen_response(message="Token error", status=1)
        info = {
            "name": user.username,
            "role": gen_roles(user),
            "avatar": ''
        }
        return gen_response(status=0, userInfo=info)
    return gen_response(code=405, message=f'method {request.method} not allowed')
