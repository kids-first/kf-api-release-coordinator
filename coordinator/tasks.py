import django_rq
import requests
from coordinator.api.models import Task, TaskService, Release, Event


@django_rq.job
def health_check(task_service_id):
    """
    Check the health of a task service

    :param task_service_id: The kf_id of the service to check
    """
    task_service = TaskService.objects.get(kf_id=task_service_id)
    task_service.health_check()


@django_rq.job
def init_release(release_id):
    """
    Initilializes a release by creating new tasks for each service and
    sending 'initialize' actions to all task services.

    :param release_id: The kf_id of the release
    """
    release = Release.objects.get(kf_id=release_id)
    task_services = TaskService.objects.all()

    release.state = 'pending'
    release.save()
    event = Event(message='release started', release=release)
    event.save()

    for service in task_services:
        if not service.enabled:
            continue
        # Create and start new task
        task = Task(task_service=service, release=release)
        task.save()
        event = Event(message="initializing new '{}' task"
                      .format(service.name),
                      task=task,
                      task_service=service,
                      release=release)
        event.save()
        django_rq.enqueue(init_task, release_id, service.kf_id, task.kf_id)


@django_rq.job
def init_task(release_id, task_service_id, task_id):
    """
    Creates a new task and requests a task service initialize it
    """
    release = Release.objects.select_related().get(kf_id=release_id)
    service = TaskService.objects.get(kf_id=task_service_id)
    task = Task.objects.get(kf_id=task_id)

    body = {
        'action': 'initialize',
        'task_id': task.kf_id,
        'release_id': release.kf_id
    }
    resp = requests.post(service.url+'/tasks', json=body)

    if resp.status_code != 200:
        release.state = 'failed'
        release.save()
        task.state = 'failed'
        event = Event(message='task for {} was rejected'.format(service.name),
                      event_type='error',
                      task=task,
                      task_service=service,
                      release=release)
        event.save()
        django_rq.enqueue(cancel_release, release_id)
        return
    else:
        task.state = 'pending'
        task.save()

        event = Event(message="task for '{}' was accepted"
                      .format(service.name),
                      task=task,
                      task_service=service,
                      release=release)
        event.save()

    # Check if we're ready to start running tasks
    if all([t.state == 'pending' for t in release.tasks.all()]):
        django_rq.enqueue(start_release, release_id)


@django_rq.job
def start_release(release_id):
    """
    Start a release by issueing the 'start' command to all task services.
    """
    release = Release.objects.select_related().get(kf_id=release_id)

    event = Event(message='all tasks were accepted, starting work',
                  release=release)
    event.save()

    for task in release.tasks.all():
        body = {
            'action': 'start',
            'task_id': task.kf_id,
            'release_id': release.kf_id
        }
        resp = requests.post(task.task_service.url+'/tasks', json=body)
        # Check that command was accepted
        if resp.status_code != 200:
            release.state = 'failed'
            release.save()
            task.state = 'failed'
            task.save()
            event = Event(message="task for '{}' failed to start"
                          .format(task.task_service.name),
                          event_type='error',
                          task=task,
                          task_service=task.task_service,
                          release=release)
            event.save()
            django_rq.enqueue(cancel_release, release_id)
            return

        task.state = resp.json()['state']
        task.save()
        event = Event(message="task for '{}' has started"
                      .format(task.task_service.name),
                      task=task,
                      task_service=task.task_service,
                      release=release)
        event.save()

    release.state = 'running'
    release.save()


@django_rq.job
def publish_release(release_id):
    """
    Publish a release by sending 'publish' action to all tasks
    """
    release = Release.objects.select_related().get(kf_id=release_id)
    event = Event(message='publishing release',
                  release=release)
    event.save()

    for task in release.tasks.all():
        body = {
            'action': 'publish',
            'task_id': task.kf_id,
            'release_id': release.kf_id
        }
        resp = requests.post(task.task_service.url+'/tasks', json=body)
        # Check that command was accepted
        if resp.status_code != 200:
            release.state = 'failed'
            release.save()
            task.state = 'failed'
            task.save()
            event = Event(message="task for '{}' failed to publish"
                          .format(task.task_service.name),
                          event_type='error',
                          task=task,
                          task_service=task.task_service,
                          release=release)
            event.save()
            django_rq.enqueue(cancel_release, release_id)
            return

        task.state = resp.json()['state']
        task.save()
        event = Event(message="task for '{}' has begun publishing"
                      .format(task.task_service.name),
                      task=task,
                      task_service=task.task_service,
                      release=release)
        event.save()


@django_rq.job
def cancel_release(release_id):
    """
    Cancels a release by sending 'cancel' action to all tasks
    """
    release = Release.objects.get(kf_id=release_id)
    event = Event(message='canceling release',
                  task=task,
                  task_service=task.task_service,
                  release=release)
    event.save()
    for task in release.tasks.all():
        body = {
            'action': 'cancel',
            'task_id': task.kf_id,
            'release_id': release.kf_id
        }
        resp = requests.post(task.task_service.url+'/tasks', json=body)
        if task.state != 'failed':
            task.state = 'canceled'
            task.save()
        event = Event(message="task for '{}' has been stopped"
                      .format(task.task_service.name),
                      task=task,
                      task_service=task.task_service,
                      release=release)
        event.save()
