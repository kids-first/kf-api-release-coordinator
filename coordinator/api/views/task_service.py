import django_rq
from rest_framework import viewsets
import django_filters.rest_framework
from rest_framework.decorators import action
from rest_framework.response import Response
from coordinator.authentication import EgoAuthentication
from coordinator.permissions import DevPermission
from coordinator.tasks import health_check
from coordinator.api.models import TaskService
from coordinator.api.serializers import TaskServiceSerializer


class TaskServiceFilter(django_filters.FilterSet):

    class Meta:
        model = TaskService
        fields = ('enabled',)


class TaskServiceViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Get a task service by `kf_id`

    create:
    Register a new task service by providing the url it is reachable at.
    The coordinator will check the provided url's /status endpoint to confirm
    that the service is reachable from the coordinator.

    list:
    Return a page of task services

    update:
    Updates a task service given a `kf_id` completely replacing any fields

    partial_update:
    Updates a task service given a `kf_id` replacing only specified fields

    destroy:
    Completely remove the task service from the coordinator.
    """
    authentication_classes = (EgoAuthentication,)
    permission_classes = (DevPermission,)
    lookup_field = 'kf_id'
    queryset = TaskService.objects.order_by('-created_at').all()
    serializer_class = TaskServiceSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = TaskServiceFilter

    @action(methods=['post'], detail=False)
    def health_checks(self, request):
        """
        Trigger tasks to check each task service's health status
        """
        task_services = TaskService.objects.all()
        for service in task_services:
            django_rq.enqueue(health_check, service.kf_id)

        return Response({'status': 'ok'}, 200)
