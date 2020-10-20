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


def parse_args(dic: str, *args, **default_args):
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
