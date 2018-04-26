from rest_framework import viewsets
from coordinator.api.models import Task,  Event
from coordinator.api.serializers import TaskSerializer


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
