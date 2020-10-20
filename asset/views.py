'''views for app asset'''

# from django.shortcuts import render
from app.utils import gen_response
# from .models import Asset

# Create your views here.


def asset_list(request):
    '''return an asset list for asset manager'''
    # if request.method == 'GET':
    #     all_asset = Asset.objects.all()
    return gen_response(code=200)
