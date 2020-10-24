''' app/utils Project 级别的 utils 函数 '''
import json
import logging

from django.http.response import JsonResponse

LOGGER = logging.getLogger('web.log')


def gen_response(**data):
    ''' gerenate json response, at response.data '''
    if 'message' in data:
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
