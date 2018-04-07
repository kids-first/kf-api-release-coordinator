from rest_framework import viewsets
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
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskServiceViewSet(viewsets.ModelViewSet):
    """
    Endpoint for task services
    """
    lookup_field = 'kf_id'
    queryset = TaskService.objects.all()
    serializer_class = TaskServiceSerializer


class ReleaseViewSet(viewsets.ModelViewSet):
    """
    endpoint for releases
    """
    lookup_field = 'kf_id'
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
