'''views of app department'''
from app.utils import gen_response
from .models import Department
# Create your views here.


def tree(request):
    ''' api/department/tree GET '''
    if request.method == 'GET':
        root = Department.objects.first().get_root()

        def visit(node):
            res = {'name': node.name,
                   'id': node.department_id,
                   'children': []
                   }
            if not node.is_leaf_node():
                children = node.get_children()
                for child in children:
                    res['children'].append(visit(child))
            return res
        res = visit(root)
        return gen_response(code=200, data=res, message='获取部门层级')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
