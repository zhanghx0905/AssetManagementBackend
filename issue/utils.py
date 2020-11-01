''' utils function for App issue '''


def get_issues_list(issues):
    ''' 根据Query Set返回issue列表 '''
    res = []
    for issue in issues:
        res.append({
            'nid': issue.id,
            'initiator': issue.initiator.username,
            'asset': f'{issue.asset.name}({issue.asset.id})',
            'type_name': issue.type_name,
            'assignee': issue.assignee_name,
            'status': issue.status,
        })
    return res
