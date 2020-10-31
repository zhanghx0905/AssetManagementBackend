''' views func for App issue '''
from issue.models import Issue
from app.utils import catch_exception, gen_response, parse_args

from asset.models import Asset


def get_issues_list(issues):
    ''' 根据Query Set返回issue列表 '''
    res = []
    for issue in issues:
        res.append({
            'nid': issue.id,
            'initiator': issue.initiator.username,
            'asset': f'{issue.asset.name}({issue.asset.id})',
            'type_name': issue.type_name,
            'assignee': issue.assignee_name
        })
    return res


@catch_exception('GET')
def handling_list(request):
    ''' api/issue/handling GET
    需要本用户处理的请求列表
    '''
    issues = Issue.objects.filter(handler=request.user)
    res = get_issues_list(issues)
    return gen_response(code=200, data=res, message=f'获取用户 {request.user.username} 待办列表')


@catch_exception('POST')
def require(request):
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
    )
    return gen_response(code=200, message=f'{request.user.username} 请求领用资产 {asset.name}')
