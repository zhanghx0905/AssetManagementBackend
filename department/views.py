'''views of app department'''
from app.utils import gen_response, visit_tree
from .models import Department
# Create your views here.


def tree(request):
    ''' api/department/tree GET '''
    if request.method == 'GET':
        root = Department.objects.first().get_root()
        res = visit_tree(root)
        return gen_response(code=200, data=res, message='获取部门层级')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
