'''views for app asset'''

# from django.shortcuts import render
from app.utils import gen_response

# Create your views here.
def asset_list(request):
    '''return an asset list for asset manager'''
    return gen_response(code=200)
