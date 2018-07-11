import django_rq
import requests
from coordinator.api.models import Task, TaskService, Release


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

    release.initialize()
    release.save()

    for service in task_services:
        if not service.enabled:
            continue
        # Create and start new task
        task = Task(task_service=service, release=release)
        task.save()

        django_rq.enqueue(init_task,
                          release.kf_id,
                          service.kf_id,
                          task.kf_id)


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
    failed = False
    resp = None
    try:
        resp = requests.post(service.url+'/tasks',
                             json=body,
                             timeout=15)
    except requests.exceptions.RequestException:
        failed = True

    if resp and resp.status_code != 200:
        failed = True

    if failed:
        release.failed()
        release.save()
        task.reject()
        task.save()
        django_rq.enqueue(cancel_release, release.kf_id, True)
        return
    else:
        task.initialize()
        task.save()

    # Check if we're ready to start running tasks
    if all([t.state == 'initialized' for t in release.tasks.all()]):
        django_rq.enqueue(start_release, release_id)


@django_rq.job
def start_release(release_id):
    """
    Start a release by issueing the 'start' command to all task services.
    """
    release = Release.objects.select_related().get(kf_id=release_id)

    release.start()
    release.save()

    for task in release.tasks.all():
        body = {
            'action': 'start',
            'task_id': task.kf_id,
            'release_id': release.kf_id
        }
        failed = False
        resp = None
        try:
            resp = requests.post(task.task_service.url+'/tasks',
                                 json=body,
                                 timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            failed = True

        # Check that command was accepted
        if resp and resp.status_code != 200:
            failed = True

        if (resp and 'state' in resp.json() and
           resp.json()['state'] != 'running'):
            failed = True

        if failed:
            release.failed()
            release.save()
            task.failed()
            task.save()
            django_rq.enqueue(cancel_release, release_id, True)
            break
        else:
            task.start()
            task.save()


@django_rq.job
def publish_release(release_id):
    """
    Publish a release by sending 'publish' action to all tasks
    """
    release = Release.objects.select_related().get(kf_id=release_id)
    release.publish()
    release.save()

    for task in release.tasks.all():
        body = {
            'action': 'publish',
            'task_id': task.kf_id,
            'release_id': release.kf_id
        }
        failed = False
        resp = None
        try:
            resp = requests.post(task.task_service.url+'/tasks',
                                 json=body,
                                 timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            failed = True

        # Check that command was accepted
        if resp and resp.status_code != 200:
            failed = True

        if (resp and 'state' in resp.json() and
           resp.json()['state'] != 'publishing'):
            failed = True

        if failed:
            release.failed()
            release.save()
            task.failed()
            task.save()
            django_rq.enqueue(cancel_release, release.kf_id, True)
            break

        task.publish()
        task.save()


@django_rq.job
def cancel_release(release_id, fail=False):
    """
    Cancels a release by sending 'cancel' action to all tasks
    """
    release = Release.objects.get(kf_id=release_id)

    for task in release.tasks.all():
        # The task may have been the one to cause the cancel/fail
        # Don't try to change its state if it's already canceled/failed
        if task.state in ['canceled', 'failed', 'rejected']:
            continue

        body = {
            'action': 'cancel',
            'task_id': task.kf_id,
            'release_id': release.kf_id
        }
        try:
            requests.post(task.task_service.url+'/tasks',
                          json=body,
                          timeout=15)
        except requests.exceptions.RequestException:
            pass

        task.cancel()
        task.save()

    if fail:
        release.failed()
    else:
        release.canceled()
    release.save()
