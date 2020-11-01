''' views func for App issue '''
from users.models import User
from issue.models import Issue
from app.utils import catch_exception, gen_response, parse_args
from asset.models import Asset
from .utils import get_issues_list


@catch_exception('GET')
def handling_list(request):
    ''' api/issue/handling GET
    需要本用户处理的请求列表
    '''
    issues = Issue.objects.filter(handler=request.user, status='DOING')

    res = get_issues_list(issues)
    return gen_response(code=200, data=res, message=f'获取用户 {request.user.username} 待办列表')


@catch_exception('GET')
def waiting_list(request):
    ''' api/issue/handling GET
    本用户等待被处理的请求列表
    '''
    issues = Issue.objects.filter(initiator=request.user)
    res = get_issues_list(issues)
    return gen_response(code=200, data=res, message=f'获取用户 {request.user.username} 在办列表')


@catch_exception('POST')
def require_issue(request):
    ''' api/issue/require POST
    领用资产
    para: nid(int) 资产nid
    '''
    nid = parse_args(request.body, 'nid')[0]
    asset: Asset = Asset.objects.get(id=int(nid))
    manager = asset.get_asset_manager()
    Issue.objects.create(
        initiator=request.user,
        handler=manager,
        asset=asset,
        type_name='REQUIRE',
        status='DOING'
    )
    return gen_response(code=200, message=f'{request.user.username} 请求领用资产 {asset.name}')


@catch_exception('POST')
def fix_issue(request):
    ''' api/issue/fix POST
    维保资产
    para: nid(int) 资产nid username(str) 维保人名
    '''
    nid, username = parse_args(request.body, 'nid', 'username')
    asset: Asset = Asset.objects.get(id=int(nid))
    handler = User.objects.get(username=username)
    Issue.objects.create(
        initiator=request.user,
        handler=handler,
        asset=asset,
        type_name='MAINTAIN',
        status='DOING'
    )
    message = f'{request.user.username} 向 {handler.username} 维保资产 {asset.name}'
    return gen_response(code=200, message=message)


@catch_exception('POST')
def transfer_issue(request):
    ''' api/issue/transfer POST
    转移资产
    para: nid(int) 资产nid username(str) 转移人名
    '''
    nid, username = parse_args(request.body, 'nid', 'username')
    asset: Asset = Asset.objects.get(id=int(nid))
    manager = asset.get_asset_manager()
    assignee = User.objects.get(username=username)
    Issue.objects.create(
        initiator=request.user,
        handler=manager,
        assignee=assignee,
        asset=asset,
        type_name='TRANSFER',
        status='DOING'
    )
    message = f'{request.user.username} 请求向 {assignee.username} 转移资产 {asset.name}'
    return gen_response(code=200, message=message)


@catch_exception('POST')
def return_issue(request):
    ''' api/issue/return POST
    退还资产
    para: nid(int) 资产nid
    '''
    nid = parse_args(request.body, 'nid')[0]
    asset: Asset = Asset.objects.get(id=int(nid))
    Issue.objects.create(
        initiator=request.user,
        handler=asset.get_asset_manager(),
        asset=asset,
        type_name='RETURN',
        status='DOING'
    )
    message = f'{request.user.username} 请求退还资产 {asset.name}'
    return gen_response(code=200, message=message)
