import pytest
from mock import Mock, patch
from coordinator.api.models import Release, Task, TaskService, Event

from coordinator.api.factories.event import EventFactory
from coordinator.api.factories.task import TaskFactory


BASE_URL = 'http://testserver'


def test_new_event(client, transactional_db, task):
    """ Test createing a new event """
    assert Task.objects.count() == 1

    # Add an event to a task
    event = {
        'event_type': 'info',
        'message': 'task created',
        'task': BASE_URL+'/tasks/' + task['kf_id']
    }
    resp = client.post(BASE_URL+'/events', data=event)
    assert resp.json()['task'].endswith(task['kf_id'])
    assert resp.json()['release'] is None
    assert resp.json()['task_service'] is None


def test_filters(client, transactional_db, event):
    assert len(client.get(BASE_URL+'/events').json()['results']) == 1
    # Get the task that was made
    resp = client.get(BASE_URL+'/tasks')
    task1 = resp.json()['results'][0]

    # Get the release that was made
    resp = client.get(BASE_URL+'/releases')
    release = resp.json()['results'][0]

    # Get the service that was made
    resp = client.get(BASE_URL+'/task-services')
    service = resp.json()['results'][0]

    # Check that there is only one event
    resp = client.get(BASE_URL+'/events')
    assert len(resp.json()['results']) == 1
    assert resp.json()['results'][0]['task'].endswith(task1['kf_id'])

    # Make a new task
    task2 = TaskFactory(
        release=Release.objects.get(kf_id=release["kf_id"]),
        task_service=TaskService.objects.get(kf_id=service["kf_id"]),
    )

    event2 = EventFactory(task=task2, release=task2.release)

    # Release should now have two events, but only one event per task
    resp = client.get(BASE_URL+'/events')
    assert len(resp.json()['results']) == 2
    resp = client.get(BASE_URL+'/events?release='+release['kf_id'])
    assert len(resp.json()['results']) == 2
    resp = client.get(BASE_URL+'/events?task='+task1['kf_id'])
    assert len(resp.json()['results']) == 1
    resp = client.get(BASE_URL+'/events?task='+task2.kf_id)
    assert len(resp.json()['results']) == 1


def test_event_for_release(client, db, worker, release):
    """ Check that there is an event created for a new release """
    worker.work(burst=True)
    assert Event.objects.filter(release_id=release['kf_id']).count() == 3
    events = [ev for ev in Event.objects.all()]
    assert ('release {}, version 0.0.0 changed from waiting to initializing'
            .format(release['kf_id']) in events[0].message)
    assert ('release {}, version 0.0.0 changed from initializing to running'
            .format(release['kf_id']) in events[1].message)
    assert ('release {}, version 0.0.0 changed from running to staged'
            .format(release['kf_id']) in events[2].message)


@pytest.mark.parametrize('field', [
    'kf_id',
    'event_type',
    'message',
    'created_at',
    'release',
    'task_service',
    'task'
])
def test_event_fields(client, db, event, field):
    resp = client.get(BASE_URL+'/events')
    task = resp.json()['results'][0]
    assert field in task


def test_event_relations(client, transactional_db, event):
    """ Test relations  """
    assert Release.objects.count() == 1
    assert TaskService.objects.count() == 1
    assert Task.objects.count() == 1
    assert Event.objects.count() == 1

    release = event['release']
    task_service = event['task_service']
    task = event['task']

    assert event['release'].endswith(Release.objects.first().kf_id)
    assert event['task_service'].endswith(TaskService.objects.first().kf_id)
    assert event['task'].endswith(Task.objects.first().kf_id)


def test_fail_event(client, db, task, worker):
    t = Task.objects.filter(kf_id=task['kf_id']).get()
    t.failed()
    t.save()
    release = client.get(task['release']).json()
    assert Event.objects.filter(release_id=release['kf_id']).count() == 1
    event = Event.objects.filter(release_id=release['kf_id']).get()

    assert event.event_type == 'error'
    assert ('task {} changed from pending to failed'
            .format(task['kf_id']) in event.message)
