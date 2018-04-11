from rest_framework import viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
import django_rq
from coordinator.api.models import Task, TaskService, Release
from coordinator.api.serializers import (
    TaskSerializer,
    TaskServiceSerializer,
    ReleaseSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    """
    Endpoint for tasks
    """
    lookup_field = 'kf_id'
    queryset = Task.objects.order_by('-created_at').all()
    serializer_class = TaskSerializer


class TaskServiceViewSet(viewsets.ModelViewSet):
    """
    Endpoint for task services
    """
    lookup_field = 'kf_id'
    queryset = TaskService.objects.order_by('-created_at').all()
    serializer_class = TaskServiceSerializer


@django_rq.job
def set_state(kf_id, state='running', delay=1):
    import time
    time.sleep(delay)
    r = Release.objects.get(kf_id=kf_id)
    r.state = state
    r.save()


class ReleaseViewSet(viewsets.ModelViewSet, UpdateModelMixin):
    """
    endpoint for releases
    """
    lookup_field = 'kf_id'
    queryset = Release.objects.order_by('-created_at').all()
    serializer_class = ReleaseSerializer

    def create(self, *args, **kwargs):
        res = super(ReleaseViewSet, self).create(*args, **kwargs)
        if res.status_code == 201:
            kf_id = res.data['kf_id']
            django_rq.enqueue(set_state, kf_id, state='running', delay=3)
            django_rq.enqueue(set_state, kf_id, state='staged', delay=8)
        return res

    @action(methods=['post'], detail=True)
    def publish(self, request, kf_id=None):
        django_rq.enqueue(set_state, kf_id, state='publishing', delay=0)
        django_rq.enqueue(set_state, kf_id, state='published', delay=5)
        return Response({
            '_status': {
                'message': 'submitted for publication',
                'code': 200,
            }
        })
