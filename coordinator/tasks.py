import django_rq
import requests
import logging
from django.conf import settings
from django.core.cache import cache
from coordinator.authentication import headers
from coordinator.api.models import Task, TaskService, Release


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@django_rq.job
def health_check(task_service_id):
    """
    Check the health of a task service

    :param task_service_id: The kf_id of the service to check
    """
    task_service = TaskService.objects.get(kf_id=task_service_id)
    task_service.refresh_from_db()
    task_service.health_check()


@django_rq.job
def status_check(task_id):
    """
    Check the status of all running and publishing tasks

    :param task_service_id: The kf_id of the service to check
    """
    task = Task.objects.get(kf_id=task_id)
    task.status_check()


@django_rq.job
def release_status_check(release_id):
    """
    Check the status of a release

    :param release_id: The kf_id of the release to check
    """
    release = Release.objects.get(kf_id=release_id)
    release.status_check()


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

    # There should always be services in a release, but if not, immediately
    # stage the release
    if not task_services:
        release.start()
        release.staged()
        release.save()
        return

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
        resp = requests.post(
            service.url + "/tasks",
            headers=headers(),
            json=body,
            timeout=settings.REQUEST_TIMEOUT,
        )
    except requests.exceptions.RequestException:
        failed = True
        logger.error(f'problem requesting task for init: {resp.content}')

    if resp and resp.status_code != 200:
        logger.error(f' invalid code from task for init: {resp.status_code}')
        failed = True

    if failed:
        release.cancel()
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
            resp = requests.post(
                task.task_service.url + "/tasks",
                headers=headers(),
                json=body,
                timeout=settings.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            logger.error(f'problem requesting task for start: {resp.content}')
            failed = True

        # Check that command was accepted
        if resp and resp.status_code != 200:
            logger.error(f'invalid code from task for start: ' +
                         '{resp.status_code}')
            failed = True

        if (resp and 'state' in resp.json() and
           resp.json()['state'] != 'running'):
            logger.error(f'invalid state returned from task for start: ' +
                         '{resp.content}')
            failed = True

        if failed:
            release.cancel()
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
    tasks = release.tasks.all()

    # Should always have at least one task service for a release, but if there
    # are none, publish skip to published
    if not tasks:
        release.complete()

    release.save()

    for task in tasks:
        body = {
            'action': 'publish',
            'task_id': task.kf_id,
            'release_id': release.kf_id
        }
        failed = False
        resp = None
        try:
            resp = requests.post(
                task.task_service.url + "/tasks",
                headers=headers(),
                json=body,
                timeout=settings.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            logger.error(f'problem requesting task for publish: ' +
                         f'{resp.content}')
            failed = True

        # Check that command was accepted
        if resp and resp.status_code != 200:
            logger.error(f'invalid code from task for publish: ' +
                         '{resp.status_code}')
            failed = True

        if (resp and 'state' in resp.json() and
           resp.json()['state'] != 'publishing'):
            logger.error(f'invalid state returned from task for publish: ' +
                         '{resp.content}')
            failed = True

        if failed:
            release.cancel()
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
            requests.post(
                task.task_service.url + "/tasks",
                headers=headers(),
                json=body,
                timeout=settings.REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException:
            pass

        task.cancel()
        task.save()

    if fail:
        release.failed()
    else:
        release.canceled()
    release.save()
