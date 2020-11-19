''' utils function for App asset '''
from app.utils import EchoDict

HISTORY_OP_TYPE = {'~': '更新', '+': '创建', '-': '删除'}
FIELD_TO_ZH = {
    'name': '资产名',
    'description': '描述',
    'parent': '父资产id',
    'status': '状态',
    'owner': '挂账人',
}
CODE_TO_ZH = EchoDict({
    'IDLE': '空闲中',
    'IN_USE': '使用中',
    'IN_MAINTAIN': '维护中',
    'RETIRED': '已清退',
})


def gen_history(record):
    ''' 根据历史记录获得历史 '''
    record_dict = {
        'user': 'unknown' if record.history_user is None else record.history_user.username,
        'time': record.history_date.strftime('%Y-%m-%d %H:%M:%S'),
        'type': HISTORY_OP_TYPE[record.history_type],
    }

    if record.history_change_reason is not None:
        record_dict['type'] = record.history_change_reason
    info = []
    if record.prev_record is not None:
        delta = record.diff_against(record.prev_record)
        for change in delta.changes:
            info.append(f"{FIELD_TO_ZH[change.field]} 从 "
                        f"{CODE_TO_ZH[change.old]} 变为 {CODE_TO_ZH[change.new]}")
    record_dict['info'] = info
    return record_dict


def get_assets_list(assets):
    ''' 根据Query Set获得资产列表 '''
    res = [asset.to_dict() for asset in assets]
    res.sort(key=lambda asset: asset['nid'])
    return res
