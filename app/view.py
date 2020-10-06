'''
Basic views
'''
import os

import prometheus_client as prometheus
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseNotFound


def serve_static(request, path='/index.html'):
    '''
    Return static files,
    as django.contrib.staticfiles is disabled in production mode.

    Actually, static files shall be served separately, for example with nginx.
    '''
    # print(path)
    path = f"{getattr(settings, 'STATICFILES_DIR')}/{path}"

    if os.path.isfile(path):
        return FileResponse(open(path, 'rb'))
    return HttpResponseNotFound()


def metrics(request):
    '''
    Serve prometheus metrics
    '''
    metrics_page = prometheus.generate_latest(prometheus.REGISTRY)
    return HttpResponse(metrics_page,
                        content_type=prometheus.CONTENT_TYPE_LATEST)
