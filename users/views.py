''' Views for App users '''
import json

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse

from .models import User


# token(str): user(User)
CUR_USERS = {}


def gen_response(**data):
    return JsonResponse(data)


def parse_args(dic: str, *args):
    dic = json.loads(dic)
    res = []
    for arg in args:
        val = dic.get(arg, None)
        if val is None:
            return (False, f"{arg} is not given")
        res.append(val)
    return (True, res)


def gen_roles(user: User) -> list:
    role = []
    if user.is_it_manager:
        role.append('IT')
    if user.is_asset_manager:
        role.append('ASSET')
    if user.is_system_manager:
        role.append('SYSTEM')
    return role


def user_list(request):
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
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name')
        if not valid:
            return gen_response(code=201, message=res)
        name = res[0]

        user = User.objects.filter(username=name)
        if not user:
            return gen_response(message='no such user', code=202)
        user[0].delete()
        return gen_response(code=200)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_exist(request):
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name')
        if not valid:
            return gen_response(code=201, message=res)
        name = res[0]

        cnt = User.objects.filter(username=name).count()
        return gen_response(code=200, exist=(cnt == 1))
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_add(request):
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
        except ValidationError as e:
            return gen_response(message=f"Validation Error of user, {e}", code=400)
        return gen_response(code=200)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_edit(request):
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
    if request.method == 'POST':
        token = request.COOKIES['Token']
        user = CUR_USERS.get(token, None)
        if user is None:
            return gen_response(message="User not online", status=1)
        CUR_USERS.pop(token)
        return gen_response(status=0)
    return gen_response(code=405, message=f'method {request.method} not allowed')


def user_info(request):
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
        return gen_response(status=0, usermessage=info)
    return gen_response(code=405, message=f'method {request.method} not allowed')
