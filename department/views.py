'''views of app department'''
from app.utils import catch_exception, gen_response, parse_args, visit_tree
from users.utils import auth_permission_required
from .models import Department


@catch_exception('GET')
@auth_permission_required('users.ASSET')
def department_tree(request):
    ''' api/department/tree GET '''
    root = Department.objects.first().get_root()
    res = visit_tree(root)
    return gen_response(code=200, data=res, message='获取部门层级')


@catch_exception('POST')
@auth_permission_required('users.ASSET')
def department_add(request):
    ''' api/department/add POST
    para: parent_id(int), name(str)
    return: code =
        200: success
    '''
    parent_id, name = parse_args(request.body, 'parent_id', 'name')
    parent = Department.objects.get(id=parent_id)
    Department.objects.create(name=name, parent=parent)
    return gen_response(code=200, message=f'添加部门 {name}')


@catch_exception('POST')
@auth_permission_required('users.ASSET')
def department_delete(request):
    ''' api/department/delete POST
    para: id(int)
    return: code =
        200: success
        201: parameter error
        202: 对应部门不存在
        203: 顶层部门不能删除
    '''
    nid = parse_args(request.body, 'id')[0]

    if int(nid) == Department.root().id:
        return gen_response(code=203, message='顶层部门不能删除')

    department = Department.objects.get(id=nid)
    department.delete()
    return gen_response(code=200, message=f'删除部门 {department.name}')


@catch_exception('POST')
@auth_permission_required('users.ASSET')
def department_edit(request):
    ''' api/department/edit POST
    para: id(int), name(str)
    return: code =
        200: success
    '''
    nid, name = parse_args(request.body, 'id', 'name')
    department = Department.objects.get(id=nid)

    old_name, department.name = department.name, name
    department.save()
    return gen_response(code=200, message=f'修改部门信息 {old_name} -> {name}')
