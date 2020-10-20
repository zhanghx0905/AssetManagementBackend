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
    ''' parse para from json str
    return valid(bool), result(list or str)
    '''
    try:
        dic = json.loads(dic)
    except json.decoder.JSONDecodeError:
        dic = {}
    res = []
    for arg in args:
        val = dic.get(arg, default_args.get(arg, None))
        if val is None:
            return (False, f"http 参数 {arg} 没有给出")
        res.append(val)
    return (True, res)
