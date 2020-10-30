'''views for app asset'''
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

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
                'now_value': asset.now_value,
                'category': asset.category.name,
                'type_name': asset.type_name,
                'description': asset.description,
                'parent': asset.parent_str,
                'child': '',
                'status': asset.status,
                'owner': asset.owner.username,
                'department': asset.department.name,
                'start_time': asset.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'service_life': asset.service_life
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
                'type_name', 'quantity', 'value',
                'name', 'category', 'description',
                'service_life', 'parent_id',
                type_name='ITEM', quantity=1,
                description='', service_life=5, parent_id=-1
            )
        except KeyError as err:
            return gen_response(code=201, message=str(err))

        for pack in pack_list:
            type_name, quantity, value, name, category, description, service_life, parent_id = pack
            try:
                category = AssetCategory.objects.get(name=category)
            except AssetCategory.DoesNotExist:
                return gen_response(message=f"资产类别 {category} 不存在", code=400)
            try:
                parent = Asset.objects.get(id=parent_id)
            except Asset.DoesNotExist:
                parent = None
            asset = Asset(
                type_name=type_name,
                quantity=quantity,
                value=value,
                name=name,
                category=category,
                description=description,
                owner=request.user,
                status='IDLE',
                service_life=service_life,
                parent=parent
            )
            try:
                asset.full_clean()
                asset.save()
            except ValidationError as error:
                return gen_response(message=str(error).replace('"', "'"), code=400)
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
    return: code = ...
    data = [
        {time(str), user(str), type(str), info(str)}, ...
    ]
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
        res = []
        for record in history:
            record_dict = {
                'user': 'unknown',
                'time': record.history_date.strftime('%Y-%m-%d %H:%M:%S'),
                'type': HISTORY_OP_TYPE[record.history_type],
            }
            if record.history_user is not None:
                record_dict['user'] = record.history_user.username
            info = []
            if record.history_type == '~':
                old_record = record.prev_record
                delta = record.diff_against(old_record)
                for change in delta.changes:
                    info.append(f"{change.field} 从 {change.old} 变为 {change.new}")
            record_dict['info'] = info
            res.append(record_dict)
        return gen_response(code=200, data=res, message=f'获取资产 {asset.name} 历史')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def asset_require(request):
    ''' api/asset/require POST
    param : nid(int)
    code =  200 success
            202 no such asset'''
    if request.method == 'POST':
        try:
            nid = parse_args(request.body, 'nid')[0]
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        try:
            asset = Asset.objects.get(id=int(nid))
        except Asset.DoesNotExist:
            return gen_response(message='资产不存在', code=202)
        asset.owner = request.user
        asset.status = 'IN_USE'
        asset.save()
        return gen_response(code=200, message=f'{request.user.username} 领用资产 {asset.name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def category_tree(request):
    ''' api/asset/category/tree GET'''
    if request.method == 'GET':
        root = AssetCategory.root()
        res = visit_tree(root)
        return gen_response(code=200, data=res, message='获取资产分类树')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def category_add(request):
    ''' api/asset/category/add POST
    para: parent_id(int), name(str)
    return: code =
        200: success
    '''
    if request.method == 'POST':
        try:
            parent_id, category_name = parse_args(request.body, 'parent_id', 'name')
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        try:
            parent = AssetCategory.objects.get(id=parent_id)
        except AssetCategory.DoesNotExist:
            return gen_response(code=202, message="id 对应父类别不存在")
        try:
            AssetCategory.objects.create(name=category_name, parent=parent)
        except IntegrityError:
            return gen_response(code=203, message="类型名不能重复")
        return gen_response(code=200, message=f'添加资产类别 {category_name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def category_delete(request):
    ''' api/asset/category/delete POST
    para: id(int)
    return: code =
        200: success
        201: parameter error
        202: 对应部门不存在
        203: 顶层部门不能删除
    '''
    if request.method == 'POST':
        try:
            category_id = parse_args(request.body, 'id')[0]
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        if int(category_id) == AssetCategory.root().id:
            return gen_response(code=203, message='顶级资产类型不能删除')
        try:
            category = AssetCategory.objects.get(id=category_id)
        except AssetCategory.DoesNotExist:
            return gen_response(code=202, message="id 对应资产类别不存在")
        category.delete()
        return gen_response(code=200, message=f'删除资产类别 {category.name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def category_edit(request):
    ''' api/asset/category/edit POST
    para: id(int), name(str)
    return: code =
        200: success
    '''
    if request.method == 'POST':
        try:
            category_id, name = parse_args(request.body, 'id', 'name')
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        try:
            category = AssetCategory.objects.get(id=category_id)
        except AssetCategory.DoesNotExist:
            return gen_response(code=202, message="id 对应资产类别不存在")

        old_name, category.name = category.name, name
        category.save()
        return gen_response(code=200, message=f'修改资产类别名 {old_name} -> {name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
