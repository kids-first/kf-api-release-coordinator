import django_rq
from rest_framework import viewsets
import django_filters.rest_framework
from rest_framework.decorators import action
from rest_framework.response import Response

from coordinator.permissions import AdminOrReadOnlyPermission
from coordinator.tasks import status_check, cancel_release
from coordinator.api.models import Task
from coordinator.api.serializers import TaskSerializer


class TaskFilter(django_filters.FilterSet):

    class Meta:
        model = Task
        fields = ('release', 'task_service', 'state')


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
    permission_classes = (AdminOrReadOnlyPermission,)
    lookup_field = 'kf_id'
    queryset = Task.objects.order_by('-created_at').all()
    serializer_class = TaskSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = TaskFilter
    http_method_names = ["get", "post", "head", "put", "patch"]

    def partial_update(self, request, kf_id=None):
        """
        Partial update of the task.
        A task service may call this endpoint to report new progress or
        that it has reached a new state.
        """
        resp = super(TaskViewSet, self).partial_update(request, kf_id)
        # If the task is failed
        if resp.data['state'] == 'failed':
            release = Task.objects.get(kf_id=kf_id).release
            django_rq.enqueue(cancel_release, release.kf_id, True)
        # If the task is canceled
        if resp.data['state'] == 'canceled':
            release = Task.objects.get(kf_id=kf_id).release
            release.cancel()
            release.save()
            django_rq.enqueue(cancel_release, release.kf_id, False)
        # If the task is being updated to staged
        if resp.data['state'] == 'staged':
            kf_id = resp.data['kf_id']
            task = Task.objects.select_related().get(kf_id=kf_id)
            # Check if all the release's tasks have been staged
            release = task.release
            if all([t.state == 'staged' for t in release.tasks.all()]):
                release.staged()
                release.save()

        # If the task is being updated to published
        elif resp.data['state'] == 'published':
            kf_id = resp.data['kf_id']
            task = Task.objects.select_related().get(kf_id=kf_id)
            # Check if all the release's tasks have been published
            release = task.release
            if all([t.state == 'published' for t in release.tasks.all()]):
                release.complete()
                release.save()
        return resp

    @action(methods=['post'], detail=False)
    def status_checks(self, request):
        """
        Trigger jobs to check each task's status
        """
        tasks = Task.objects.filter(state__in=['running', 'publishing'])
        for task in tasks:
            django_rq.enqueue(status_check, task.kf_id)

        return Response({'status': 'ok',
                         'message': f'{len(tasks)} task to check'}, 200)
