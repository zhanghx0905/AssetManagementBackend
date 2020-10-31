'''
app/utils Project 级别的 utils 函数
本文件下的函数一般不用特别测试
'''
import json
import logging
from functools import partial

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http.response import JsonResponse
from django.test.testcases import TestCase

LOGGER = logging.getLogger('web.log')


def gen_response(**data):
    ''' gerenate json response, at response.data '''
    if 'message' in data:
        if 'code' in data and data['code'] != 200:
            LOGGER.warning(data['message'])
        else:
            LOGGER.info(data['message'])
    return JsonResponse(data)


def parse_args(dic: str, *args, **default_args) -> list:
    """
    parse POST parameters from json strings

    参数:
        dic: json 字符串
        args: 变长参数，接收要解析出的字段
        default_args: 关键字参数，接受字段的默认值
    return result(List)

    例:
    try:
        name, pwd = parse_args(request.body, 'name', 'password', name='me')
    except KeyError as error:
        pass

    如果请求体中没有 name 字段，返回的 name 就是默认值 me
    如果请求体中没有 password 字段，会抛出 KeyError 错误
    """
    try:
        dic = json.loads(dic)
    except json.decoder.JSONDecodeError:
        dic = {}
    res = []
    for arg in args:
        val = dic.get(arg, default_args.get(arg, None))
        if val is None:
            raise KeyError(f"http 参数 {arg} 没有给出")
        res.append(val)
    return res


def parse_list(dic: str, *args, **default_args):
    '''parse_arg 的列表版本，注意列表应对应在data字段'''
    try:
        dic = json.loads(dic)
    except json.decoder.JSONDecodeError:
        return []
    res_list = []
    for item in dic['data']:
        res = []
        for arg in args:
            val = item.get(arg, default_args.get(arg, None))
            if val is None:
                raise KeyError(f"http 参数 {arg} 没有给出")
            res.append(val)
        res_list.append(res)
    return res_list


def visit_tree(node):
    '''
    transform a mptt to dict
    '''
    res = {'name': node.name, 'id': node.id, 'children': []}
    if not node.is_leaf_node():
        children = node.get_children()
        for child in children:
            res['children'].append(visit_tree(child))
    return res


def catch_exception(*valid_http_methods):
    '''
    用装饰器捕获一些常见的异常并处理，降低异常处理代码量

    捕获的错误包括:
        - Http 方法错误
        - POST 请求体参数错误
        - 数据库对应表项不存在错误
        - 数据库表项格式错误

    例:
    @catch_exception('GET')
    def fun(request):
        pass
    '''
    error_response = partial(gen_response, status=1)

    def decorator(func):
        def inner(request, *args, **kwargs):
            if request.method not in valid_http_methods:
                return error_response(message=f'Http 方法 {request.method} 是不被允许的', code=405)
            try:
                response = func(request, *args, **kwargs)
            except KeyError as err:   # POST 请求体错误
                return error_response(message=str(err), code=201)
            except ObjectDoesNotExist as err:   # 数据库对应表项不存在错误
                return error_response(message=str(err), code=202)
            except ValidationError as err:  # 数据库格式错误
                return error_response(message=str(err).replace('"', "'"), code=400)
            return response
        return inner
    return decorator


def init_test(test: TestCase):
    ''' 在测试模块的setUp函数中调用，
    以初始化资源并登录admin '''
    from users.apps import init_department, add_admin
    init_department()
    add_admin()
    response = test.client.post('/api/user/login',
                                data=json.dumps({'username': 'admin', 'password': 'admin'}),
                                content_type='json')
    test.client.cookies['Token'] = response.json()['token']
