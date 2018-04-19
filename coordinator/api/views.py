import django_rq
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from coordinator.tasks import init_release, publish_release, health_check
from coordinator.api.models import Task, TaskService, Release, Event
from coordinator.api.serializers import (
    TaskSerializer,
    TaskServiceSerializer,
    ReleaseSerializer,
    EventSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    """
    Endpoint for tasks
    """
    lookup_field = 'kf_id'
    queryset = Task.objects.order_by('-created_at').all()
    serializer_class = TaskSerializer

    def partial_update(self, request, kf_id=None):
        resp = super(TaskViewSet, self).partial_update(request, kf_id)
        # If the task is being updated to staged
        if resp.data['state'] == 'staged':
            kf_id = resp.data['kf_id']
            task = Task.objects.select_related().get(kf_id=kf_id)
            release = task.release
            # Check if all the release's tasks have been staged
            if all([t.state == 'staged' for t in release.tasks.all()]):
                release.state = 'staged'
                release.save()
        # If the task is being updated to published
        elif resp.data['state'] == 'published':
            kf_id = resp.data['kf_id']
            task = Task.objects.select_related().get(kf_id=kf_id)
            release = task.release
            # Check if all the release's tasks have been published
            if all([t.state == 'published' for t in release.tasks.all()]):
                release.state = 'published'
                release.save()
        return resp


class TaskServiceViewSet(viewsets.ModelViewSet):
    """
    Endpoint for task services
    """
    lookup_field = 'kf_id'
    queryset = TaskService.objects.order_by('-created_at').all()
    serializer_class = TaskServiceSerializer

    @action(methods=['post'], detail=False)
    def health_checks(self, request):
        task_services = TaskService.objects.all()
        for service in task_services:
            django_rq.enqueue(health_check, service.kf_id)

        return Response({'status': 'ok'}, 200)


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
        release = Release.objects.get(kf_id=kf_id)
        release.state = 'publishing'
        release.save()
        django_rq.enqueue(publish_release, release.kf_id)
        return self.retrieve(request, kf_id)


class EventViewSet(viewsets.ModelViewSet):
    """
    endpoint for events
    """
    lookup_field = 'kf_id'
    serializer_class = EventSerializer

    def get_queryset(self):
        """
        Filter by relase, task_sevice, and/or task
        """
        queryset = Event.objects.order_by('-created_at')

        for field_name in ['release', 'task_service', 'task']:
            field = self.request.query_params.get(field_name, None)
            if field is not None:
                kwargs = {field_name: field}
                queryset = queryset.filter(**kwargs)

        return queryset
