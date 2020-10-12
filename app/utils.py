''' app/utils Project 级别的 utils 函数 '''
from django.http.response import JsonResponse


def gen_response(**data):
    ''' gerenate json response, at response.data '''
    return JsonResponse(data)
