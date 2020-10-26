'''views for app asset'''
from django.core.exceptions import ValidationError

from app.utils import gen_response, parse_args, parse_list, visit_tree
from users.models import User
from .models import Asset, AssetCatagory


def asset_list(request):
    '''api/asset/list GET
    return an asset list for asset manager'''
    if request.method == 'GET':
        all_asset = Asset.objects.all()
        res = []
        for asset in all_asset:
            res.append({
                'nid': asset.id,
                'name': asset.name,
                'quantity': asset.quantity,
                'value': asset.value,
                'is_quantity': asset.is_quantity,
                'description': asset.description,
                'parent': asset.parent,
                'child': asset.child,
                'status': asset.status,
                'owner': asset.owner.username,
                'department': asset.department.name,
                'start_time': asset.start_time.timestamp()
            })
        return gen_response(code=200, data=res, message='获取资产列表')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def asset_add(request):
    '''  api/asset/add POST
    资产管理员添加资产
    return: code =
        200: success
        201: parameter error
        400: Validation Error when saving user
    '''
    if request.method == 'POST':
        try:
            pack_list = parse_list(
                request.body,
                'is_quantity',
                'quantity',
                'value',
                'name',
                'description',
                'parent',
                'owner',
                is_quantity=True,
                quantity=1,
                value=1,
                description='...',
                parent='',
                owner='',
            )

        except KeyError as err:
            return gen_response(code=201, message=str(err))

        for pack in pack_list:
            is_quantity, quantity, value, name, description, parent, owner = pack
            try:
                owner = User.objects.get(username=owner)
            except User.DoesNotExist:
                owner = User.admin()
            asset = Asset(
                is_quantity=is_quantity,
                quantity=quantity,
                value=value,
                name=name,
                description=description,
                parent=parent,
                owner=owner,
                status='IDLE'
            )

            try:
                asset.full_clean()
                asset.save()
            except ValidationError as error:
                return gen_response(message=str(error), code=400)
        return gen_response(code=200, message=f'添加资产{len(pack_list)}条')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def asset_edit(request):
    '''  api/asset/edit POST
    编辑资产
    可编辑的条目有：name, description, owner, department, status, quantity, value
    return: code =
        200: success
        201: parameter error
        202：no such user
    '''
    if request.method == 'POST':
        try:
            pack = parse_args(request.body, 'nid', 'name', 'description',
                              'owner', 'status', 'quantity', 'value')
            nid = pack[0]
        except KeyError as err:
            return gen_response(code=201, message=str(err))

        try:
            asset = Asset.objects.get(id=nid)
        except Asset.DoesNotExist:
            return gen_response(message='资产不存在', code=202)
        _, asset.name, asset.description, owner, asset.status, asset.quantity, asset.value = pack
        try:
            owner = User.objects.get(username=owner)
        except User.DoesNotExist:
            owner = User.admin()
        asset.owner = owner

        asset.save()

        return gen_response(code=200, message=f'{asset.name} 信息修改')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def catagory_tree(request):
    ''' api/asset/catagory GET'''
    if request.method == 'GET':
        root = AssetCatagory.root()
        res = visit_tree(root)
        return gen_response(code=200, data=res, message='获取资产分类树')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
