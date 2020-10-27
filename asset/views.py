'''views for app asset'''
from django.core.exceptions import ValidationError

from app.utils import gen_response, parse_args, parse_list, visit_tree
from .models import Asset, AssetCategory


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
                'category': asset.category.name,
                'type_name': asset.type_name,
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
    资产管理员添加资产，需要提供的条目：
    type_name, quantity, value, name, category, description
    return: code =
        200: success
        201: parameter error
        400: Validation Error when saving asset
    '''
    if request.method == 'POST':
        try:
            pack_list = parse_list(
                request.body,
                'type_name',
                'quantity',
                'value',
                'name',
                'category',
                'description'
            )
        except KeyError as err:
            return gen_response(code=201, message=str(err))

        for pack in pack_list:
            type_name, quantity, value, name, category, description = pack
            try:
                category = AssetCategory.objects.get(name=category)
            except KeyError as err:
                # 录入的资产名称不存在，跳过这一条
                continue

            asset = Asset(
                type_name=type_name,
                quantity=quantity,
                value=value,
                name=name,
                category=category,
                description=description,
                owner=request.user,
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
    可编辑的条目有：name, description
    return: code =
        200: success
        201: parameter error
        202：no such asset
    '''
    if request.method == 'POST':
        try:
            nid, name, description = parse_args(
                request.body, 'nid', 'name', 'description')
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        try:
            asset = Asset.objects.get(id=nid)
        except Asset.DoesNotExist:
            return gen_response(message='资产不存在', code=202)
        asset.name = name
        asset.description = description
        asset.save()
        return gen_response(code=200, message=f'{asset.name} 信息修改')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


HISTORY_OP_TYPE = {'~': '更新', '+': '创建', '-': '删除'}


def asset_history(request):
    ''' api/asset/history POST
    para: nid(int)
    '''
    if request.method == 'POST':
        try:
            nid = parse_args(request.body, 'nid')[0]
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        try:
            asset = Asset.objects.get(id=nid)
        except Asset.DoesNotExist:
            return gen_response(message='资产不存在', code=202)

        history = asset.history.all()
        records = []

        for record in history:
            user = ''
            if record.history_user is not None:
                user = record.history_user.username

            record_str = (f"{record.history_date} {HISTORY_OP_TYPE[record.history_type]} "
                          f"{user}\n")
            if record.history_type == '~':
                old_record = record.prev_record
                delta = record.diff_against(old_record)
                for change in delta.changes:
                    record_str += f"\t{change.field} 从 {change.old} 变为 {change.new}\n"
            records.append(record_str)
        return gen_response(code=200, data=records, message=f'获取资产 {asset.name} 历史')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def category_tree(request):
    ''' api/asset/category GET'''
    if request.method == 'GET':
        root = AssetCategory.root()
        res = visit_tree(root)
        return gen_response(code=200, data=res, message='获取资产分类树')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
