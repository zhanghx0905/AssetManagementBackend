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
    ''' api/issue/waiting GET
    本用户等待被处理的请求列表
    '''
    issues = Issue.objects.filter(initiator=request.user)
    res = get_issues_list(issues)
    return gen_response(code=200, data=res, message=f'获取用户 {request.user.username} 在办列表')


@catch_exception('POST')
def issue_require(request):
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
def issue_fix(request):
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
    # 更新资产状态
    asset.owner = handler
    asset.status = 'IN_MAINTAIN'
    asset.save()

    message = f'{request.user.username} 向 {handler.username} 维保资产 {asset.name}'
    return gen_response(code=200, message=message)


@catch_exception('POST')
def issue_transfer(request):
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
def issue_return(request):
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


@catch_exception('POST')
def issue_handle(request):
    ''' api/issue/handle POST
    处理代办issue
    para:
        nid(int): issue id
        success(bool): 批准或拒绝
    '''
    def require_success(asset: Asset, issue: Issue):
        ''' 领用成功后 '''
        asset.owner = issue.initiator
        asset.status = 'IN_USE'

    def fix(asset: Asset, issue: Issue):
        ''' 资产维保 成功或失败 后 '''
        asset.owner = issue.initiator
        asset.status = 'IN_USE'

    def return_success(asset: Asset, issue: Issue):
        ''' 资产退还成功后 '''
        asset.owner = issue.handler
        asset.status = 'IDLE'

    def transfer_success(asset: Asset, issue: Issue):
        ''' 资产转移成功后 '''
        asset.owner = issue.assignee

    issue_id, success = parse_args(request.body, 'nid', 'success')

    issue: Issue = Issue.objects.get(id=issue_id)
    issue.status = 'SUCCESS' if success else 'FAIL'
    issue.save()

    asset = issue.asset
    if issue.type_name == 'MAINTAIN':
        fix(asset, issue)
    elif success and issue.type_name == 'REQUIRE':
        require_success(asset, issue)
    elif success and issue.type_name == 'TRANSFER':
        transfer_success(asset, issue)
    elif success and issue.type_name == 'RETURN':
        return_success(asset, issue)
    asset.save()

    return gen_response(code=200, message=f"{request.user.username} 处理待办事项")


@catch_exception('POST')
def issue_exist(request):
    ''' api/issue/exist POST
    查询由该用户发起的某类待办issue是否已存在。
    para:
        asset_id(int): 资产id
    return: exist(bool)
    '''
    asset_id = parse_args(request.body, 'asset_id')[0]
    asset: Asset = Asset.objects.get(id=asset_id)
    exist = False
    if Issue.objects.filter(initiator=request.user,
                            asset=asset, status='DOING').exists():
        exist = True
    return gen_response(code=200, exist=exist, messgae="查询事项是否存在")


@catch_exception('POST')
def issue_delete(request):
    ''' api/issue/delete POST
    删除issue.
    para:
        nid(int): issue id
    '''
    issue_id = parse_args(request.body, 'nid')[0]
    issue: Issue = Issue.objects.get(id=issue_id)
    issue.delete()
    return gen_response(code=200, message="删除事项")
