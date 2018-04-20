import django_rq
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.utils import swagger_auto_schema
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
    retrieve:
    Return a task given its `kf_id`

    list:
    Returns a page of tasks

    create:
    Creates a new task in the `waiting` state

    update:
    Updates a task given a `kf_id` completely replacing any fields

    destroy:
    Removes a task entirely
    """
    lookup_field = 'kf_id'
    queryset = Task.objects.order_by('-created_at').all()
    serializer_class = TaskSerializer

    def partial_update(self, request, kf_id=None):
        """
        Partial update of the task.
        A task service may call this endpoint to report new progress or
        that it has reached a new state.
        """
        resp = super(TaskViewSet, self).partial_update(request, kf_id)
        # If the task is being updated to staged
        if resp.data['state'] == 'staged':
            kf_id = resp.data['kf_id']
            task = Task.objects.select_related().get(kf_id=kf_id)
            release = task.release
            event = Event(message="task for '{}' is staged"
                          .format(task.task_service.name),
                          task=task,
                          task_service=task.task_service,
                          release=release)
            event.save()
            # Check if all the release's tasks have been staged
            if all([t.state == 'staged' for t in release.tasks.all()]):
                release.state = 'staged'
                release.save()
                event = Event(message="release staged",
                              release=release)
                event.save()
        # If the task is being updated to published
        elif resp.data['state'] == 'published':
            kf_id = resp.data['kf_id']
            task = Task.objects.select_related().get(kf_id=kf_id)
            release = task.release
            event = Event(message="task for '{}' is published"
                          .format(task.task_service.name),
                          task=task,
                          task_service=task.task_service,
                          release=release)
            event.save()
            # Check if all the release's tasks have been published
            if all([t.state == 'published' for t in release.tasks.all()]):
                release.state = 'published'
                release.save()
                event = Event(message="release published",
                              release=release)
                event.save()
        return resp


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
    lookup_field = 'kf_id'
    queryset = TaskService.objects.order_by('-created_at').all()
    serializer_class = TaskServiceSerializer

    @action(methods=['post'], detail=False)
    def health_checks(self, request):
        """
        Trigger tasks to check each task service's health status
        """
        task_services = TaskService.objects.all()
        for service in task_services:
            django_rq.enqueue(health_check, service.kf_id)

        return Response({'status': 'ok'}, 200)


class ReleaseViewSet(viewsets.ModelViewSet, UpdateModelMixin):
    """
    retrieve:
    Get a release by `kf_id`

    list:
    Return a page of releases

    update:
    Updates a release given a `kf_id` completely replacing any fields

    partial_update:
    Updates a release given a `kf_id` replacing only specified fields
    """
    lookup_field = 'kf_id'
    queryset = Release.objects.order_by('-created_at').all()
    serializer_class = ReleaseSerializer

    def create(self, *args, **kwargs):
        """
        Create a new release given an array of study ids. This will trigger
        the begining of the release process.
        """
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
        """
        Begin the publish process for the release given a `kf_id`.
        Release must be in the `staged` state to begin publishing.
        """
        release = Release.objects.get(kf_id=kf_id)
        if release.state != 'staged':
            return self.retrieve(request, kf_id)
        release.state = 'publishing'
        release.save()
        django_rq.enqueue(publish_release, release.kf_id)
        return self.retrieve(request, kf_id)


class EventViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Get an event by `kf_id`

    create:
    Register a new event

    list:
    Return a page of events

    update:
    Updates an event  given a `kf_id` completely replacing any fields

    partial_update:
    Updates an event given a `kf_id` replacing only specified fields

    destroy:
    Completely remove the event from the coordinator.
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


class SwaggerSchema(OpenAPISchemaGenerator):
    """ Custom schema generator to inject x-logo and remove security """
    def get_schema(self, request=None, public=False):
        schema = super(SwaggerSchema, self).get_schema(request, public)
        schema['info']['x-logo'] = {'url': '/static/kf_releasecoordinator.png'}
        del schema['security']
        del schema['securityDefinitions']
        return schema
