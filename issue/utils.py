''' utils function for App issue '''


def get_issues_list(issues):
    ''' 根据Query Set返回issue列表 '''
    return [issue.to_dict() for issue in issues]
