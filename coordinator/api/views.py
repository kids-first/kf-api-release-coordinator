import django_rq
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from coordinator.tasks import init_release
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


class ReleaseViewSet(viewsets.ModelViewSet, UpdateModelMixin):
    """
    endpoint for releases
    """
    lookup_field = 'kf_id'
    queryset = Release.objects.order_by('-created_at').all()
    serializer_class = ReleaseSerializer

    def create(self, *args, **kwargs):
        """ Creates a release and starts the release process """
        res = super(ReleaseViewSet, self).create(*args, **kwargs)
        if res.status_code == 201:
            kf_id = res.data['kf_id']
            django_rq.enqueue(init_release, kf_id)
        return res

    def destroy(self, request, kf_id=None):
        """
        Cancel a release

        When a release is cancelled:
        - All running tasks should sent a cancel action
        - The release should not be deleted
        """
        try:
            release = Release.objects.get(kf_id=kf_id)
        except ObjectDoesNotExist:
            return Response({}, status=404)

        release.state = 'canceled'
        release.save()
        # Do other cancel logic here
        return self.retrieve(request, kf_id)

    @action(methods=['post'], detail=True)
    def publish(self, request, kf_id=None):
        return Response({
            '_status': {
                'message': 'submitted for publication',
                'code': 200,
            }
        })
