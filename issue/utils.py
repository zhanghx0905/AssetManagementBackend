''' utils function for App issue '''


def get_issues_list(issues):
    ''' 根据Query Set返回issue列表 '''
    res = [issue.to_dict() for issue in issues]
    return res
