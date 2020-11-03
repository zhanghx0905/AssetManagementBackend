''' utils function for App asset '''
from .models import AssetCustomAttr

HISTORY_OP_TYPE = {'~': '更新', '+': '创建', '-': '删除'}


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
            info.append(f"{change.field} 从 {change.old} 变为 {change.new}")
    record_dict['info'] = info
    return record_dict


def get_assets_list(assets):
    ''' 根据Query Set获得资产列表 '''
    res = []
    for asset in assets:
        res.append({
            'nid': asset.id,
            'name': asset.name,
            'quantity': asset.quantity,
            'value': asset.value,
            'now_value': asset.now_value,
            'category': asset.category.name,
            'type_name': asset.type_name,
            'description': asset.description,
            'parent_id': asset.parent_id_,
            'parent': asset.parent_formated,
            'children': asset.children_formated,
            'status': asset.status,
            'owner': asset.owner.username,
            'department': asset.department.name,
            'start_time': asset.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'service_life': asset.service_life,
            'custom': AssetCustomAttr.get_custom_attrs(asset),
        })
    return res
