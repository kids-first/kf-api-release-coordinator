from rest_framework import viewsets
from rest_framework.mixins import UpdateModelMixin
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


