''' utils function for App asset '''

HISTORY_OP_TYPE = {'~': '更新', '+': '创建', '-': '删除'}


def gen_history(record):
    ''' 根据历史记录获得历史 '''
    record_dict = {
        'user': 'unknown',
        'time': record.history_date.strftime('%Y-%m-%d %H:%M:%S'),
        'type': HISTORY_OP_TYPE[record.history_type],
    }
    if record.history_user is not None:
        record_dict['user'] = record.history_user.username
    info = []
    if record.history_type == '~':
        delta = record.diff_against(record.prev_record)
        for change in delta.changes:
            info.append(f"{change.field} 从 {change.old} 变为 {change.new}")
    record_dict['info'] = info
    return record_dict
