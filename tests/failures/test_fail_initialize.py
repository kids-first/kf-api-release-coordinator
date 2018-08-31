import os
import json
import pytest
import mock
import requests
from coordinator.api.models import Release, Task, TaskService, Event


BASE_URL = 'http://testserver'


with open(os.path.join(os.path.dirname(__file__), '../dev_token.txt')) as f:
    DEV_TOKEN = f.read().strip()


def init_release(client, worker):
    """
    Initialize a release
    """
    release = {
        'name': 'First release',
        'description': 'Testing',
        'studies': ['SD_00000001'],
        'tags': []
    }
    resp = client.post(BASE_URL+'/releases',
                       data=release,
                       headers={'Authorization': 'Bearer '+DEV_TOKEN})

    # Do work
    worker.work(burst=True)
    return resp


def check_common(client):
    """
    Common checks
    """
    # Check task state
    resp = client.get(BASE_URL+'/tasks')
    assert len(resp.json()['results']) == 1
    task = resp.json()['results'][0]
    assert task['state'] == 'rejected'

    # Check release state
    resp = client.get(BASE_URL+'/releases')
    assert len(resp.json()['results']) == 1
    release = resp.json()['results'][0]
    assert release['state'] == 'failed'

    # Check events
    task_id = task['kf_id']
    task = Task.objects.filter(kf_id=task_id).get()
    assert Event.objects.filter(task_id=task_id).count() == 1
    event = Event.objects.filter(task_id=task_id).get()
    assert event.event_type == 'error'

    assert Event.objects.count() == 4


def test_fail_initialize_500(client, transactional_db,
                             mocker, worker, task_service, study):
    """
    Test case when a task is rejected from returning a non-200 repsonse
    when an `initialize` action is sent to it.
    """
    mock_task_requests = mocker.patch('coordinator.tasks.requests')
    mock_task_action = mock.Mock()
    mock_task_action.status_code = 500
    mock_task_action.json.return_value = {'message': 'internal server error'}
    mock_task_requests.post.return_value = mock_task_action

    release = init_release(client, worker)
    check_common(client)


def test_fail_initialize_connection_err(client, transactional_db,
                                        mocker, worker, task_service, study):
    """
    Test case when a task is rejected from returning a non-200 repsonse
    when an `initialize` action is sent to it.
    """
    mock_task_requests = mocker.patch('coordinator.tasks.requests')
    mock_task_action = mock.Mock()
    # NB We must use the mocked exception class, not the requests exception
    exc = mock_task_requests.exceptions.ConnectionError()
    mock_task_requests.post.side_effect = exc

    release = init_release(client, worker)
    check_common(client)


def test_fail_initialize_timeout(client, transactional_db,
                                 mocker, worker, task_service, study):
    """
    Test case when a task is rejected from a timed-out request
    """
    mock_task_requests = mocker.patch('coordinator.tasks.requests')
    mock_task_action = mock.Mock()
    # NB We must use the mocked exception class, not the requests exception
    exc = mock_task_requests.exceptions.TimeoutError()
    mock_task_requests.post.side_effect = exc

    release = init_release(client, worker)
    check_common(client)
