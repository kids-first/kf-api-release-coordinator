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
        'studies': ['SD_00000000'],
        'tags': []
    }
    resp = client.post(BASE_URL+'/releases',
                       data=release,
                       headers={'Authorization': 'Bearer '+DEV_TOKEN})

    # Do work
    worker.work(burst=True)
    return resp


def test_fail_running(admin_client, client, transactional_db, mocker,
                      worker, task_service):
    """
    Test when a release fails do to a task reporting itself as failed

    The task that fails should be in a failed state
    The other task should be in a canceled state after being canceled by coord
    The release should be in a failed state as one of its tasks have failed
    """
    mock_task_requests = mocker.patch('coordinator.tasks.requests')
    mock_task_action = mock.Mock()
    mock_task_action.status_code = 200
    mock_task_action.json.return_value = {'state': 'running'}
    mock_task_requests.post.return_value = mock_task_action

    # Make another task_service
    service = {
        'name': 'test service 2',
        'url': 'http://ts2.com',
        'author': 'daniel@d3b.center',
        'description': 'lorem ipsum',
        'enabled': True
    }
    with mock.patch('coordinator.api.validators.requests') as mock_requests:
        mock_resp = mock.Mock()
        mock_resp.content = str.encode('{"name": "test"}')
        mock_resp.status_code = 200
        mock_requests.get.return_value = mock_resp
        resp = admin_client.post(BASE_URL+'/task-services', data=service)

    resp = client.get(BASE_URL+'/task-services')
    assert len(resp.json()['results']) == 2

    init_release(client, worker)

    resp = client.get(BASE_URL+'/releases')
    assert len(resp.json()['results'][0]['tasks']) == 2

    # Fail one of the tasks
    resp = client.get(BASE_URL+'/tasks')
    task = resp.json()['results'][0]

    # Fail the task from the task service
    resp = client.patch(BASE_URL+'/tasks/'+task['kf_id'],
                        json.dumps({'state': 'failed'}),
                        content_type='application/json')

    worker.work(burst=True)

    # Check release state
    resp = client.get(BASE_URL+'/releases')
    assert resp.json()['results'][0]['state'] == 'failed'

    # Check tasks' state
    resp = client.get(BASE_URL+'/tasks/'+task['kf_id'])
    assert resp.json()['state'] == 'failed'

    resp = client.get(BASE_URL+'/tasks')
    task = resp.json()['results'][1]
    assert task['state'] == 'canceled'


def test_cancel_running(admin_client, client, transactional_db, mocker,
                        worker, task_service):
    """
    Test when a release is canceled due to one of its tasks being canceled
    """
    mock_task_requests = mocker.patch('coordinator.tasks.requests')
    mock_task_action = mock.Mock()
    mock_task_action.status_code = 200
    mock_task_action.json.return_value = {'state': 'running'}
    mock_task_requests.post.return_value = mock_task_action

    # Make another task_service
    service = {
        'name': 'test service 2',
        'url': 'http://ts2.com',
        'author': 'daniel@d3b.center',
        'description': 'lorem ipsum',
        'enabled': True
    }
    with mock.patch('coordinator.api.validators.requests') as mock_requests:
        mock_resp = mock.Mock()
        mock_resp.content = str.encode('{"name": "test"}')
        mock_resp.status_code = 200
        mock_requests.get.return_value = mock_resp
        resp = admin_client.post(BASE_URL+'/task-services', data=service)

    resp = client.get(BASE_URL+'/task-services')
    assert len(resp.json()['results']) == 2

    init_release(client, worker)

    resp = client.get(BASE_URL+'/releases')
    assert len(resp.json()['results'][0]['tasks']) == 2

    # Fail one of the tasks
    resp = client.get(BASE_URL+'/tasks')
    task = resp.json()['results'][0]

    # Fail the task from the task service
    resp = client.patch(BASE_URL+'/tasks/'+task['kf_id'],
                        json.dumps({'state': 'canceled'}),
                        content_type='application/json')

    worker.work(burst=True)

    # Check release state
    resp = client.get(BASE_URL+'/releases')
    assert resp.json()['results'][0]['state'] == 'canceled'

    # Check tasks' state
    resp = client.get(BASE_URL+'/tasks/'+task['kf_id'])
    assert resp.json()['state'] == 'canceled'

    resp = client.get(BASE_URL+'/tasks')
    task = resp.json()['results'][1]
    assert task['state'] == 'canceled'
