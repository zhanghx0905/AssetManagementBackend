'''views of app department'''
from app.utils import gen_response, parse_args, visit_tree
from .models import Department


def tree(request):
    ''' api/department/tree GET '''
    if request.method == 'GET':
        root = Department.objects.first().get_root()
        res = visit_tree(root)
        return gen_response(code=200, data=res, message='获取部门层级')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def add(request):
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
        parent = Department.objects.get(id=parent_id)
        Department.objects.create(name=name, parent=parent)
        return gen_response(code=200, message=f'添加部门 {parent.name} -> {name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
