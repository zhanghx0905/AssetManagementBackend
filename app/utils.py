''' app/utils Project 级别的 utils 函数 '''
import json
from django.http.response import JsonResponse


def gen_response(**data):
    ''' gerenate json response, at response.data '''
    return JsonResponse(data)


def parse_args(dic: str, *args, **default_args):
    ''' parse para from json str 
    return valid(bool), result(list or str)
    '''
    dic = json.loads(dic)
    res = []
    for arg in args:
        val = dic.get(arg, default_args.get(arg, None))
        if val is None:
            return (False, f"{arg} is not given")
        res.append(val)
    return (True, res)
