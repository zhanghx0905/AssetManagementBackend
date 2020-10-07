from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse

from .models import User


def gen_response(code: int, data: str):
    return JsonResponse({
        'code': code,
        'data': data
    }, status=code)


def user_register(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        pwd = request.POST.get('password', None)
        if name is None or pwd is None:
            return gen_response(400, 'name or password are not given')
        pwd = make_password(pwd, None)

        user = User(name=name, pwd=pwd)
        try:
            user.full_clean()
            user.save()
        except ValidationError as e:
            return gen_response(400, f"Validation Error of user: {e}")
        return gen_response(200, pwd)
    return gen_response(405, f'method {request.method} not allowed')


def user_login(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        pwd = request.POST.get('password', None)
        if name is None or pwd is None:
            return gen_response(400, 'name or password are not given')
        target_user = User.objects.filter(name=name)
        if len(target_user) != 1:
            return gen_response(400, 'the user does not exist')
        target_user = target_user[0]
        if not check_password(pwd, target_user.pwd):
            return gen_response(400, 'the password invalid')
        return gen_response(200, 'OK')
    return gen_response(405, f'method {request.method} not allowed')
