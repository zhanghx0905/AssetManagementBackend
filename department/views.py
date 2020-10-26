'''views of app department'''
from app.utils import gen_response, parse_args, visit_tree
from .models import Department


def department_tree(request):
    ''' api/department/tree GET '''
    if request.method == 'GET':
        root = Department.objects.first().get_root()
        res = visit_tree(root)
        return gen_response(code=200, data=res, message='获取部门层级')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def department_add(request):
    ''' api/department/add POST
    para: parent_id(int), name(str)
    return: code =
        200: success
    '''
    if request.method == 'POST':
        try:
            parent_id, name = parse_args(request.body, 'parent_id', 'name')
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        try:
            parent = Department.objects.get(id=parent_id)
        except Department.DoesNotExist:
            return gen_response(code=202, message="id 对应父部门不存在")
        Department.objects.create(name=name, parent=parent)
        return gen_response(code=200, message=f'添加部门 {name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def department_delete(request):
    ''' api/department/delete POST
    para: id(int)
    return: code =
        200: success
        201: parameter error
        202: 对应部门不存在
        203: 顶层部门不能删除
    '''
    if request.method == 'POST':
        try:
            nid = parse_args(request.body, 'id')[0]
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        if int(nid) == Department.root().id:
            return gen_response(code=203, message='顶层部门不能删除')
        try:
            department = Department.objects.get(id=nid)
        except Department.DoesNotExist:
            return gen_response(code=202, message="id 对应部门不存在")
        department.delete()
        return gen_response(code=200, message=f'删除部门 {department.name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def department_edit(request):
    ''' api/department/edit POST
    para: id(int), name(str)
    return: code =
        200: success
    '''
    if request.method == 'POST':
        try:
            nid, name = parse_args(request.body, 'id', 'name')
        except KeyError as err:
            return gen_response(code=201, message=str(err))
        try:
            department = Department.objects.get(id=nid)
        except Department.DoesNotExist:
            return gen_response(code=202, message="id 对应部门不存在")

        old_name, department.name = department.name, name
        department.save()
        return gen_response(code=200, message=f'修改部门信息 {old_name} -> {name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
