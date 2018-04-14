import json
import pytest
import mock
from django_rq import get_worker
from coordinator.api.models import Release, Task, TaskService


BASE_URL = 'http://testserver'

def test_full_release(client, transactional_db, mocker):
    """
    Test a full release:
    1) Create task service
    2) Create release
    """
    mock_requests = mocker.patch('coordinator.api.models.requests')
    mock_resp = mock.Mock()
    mock_resp.status_code = 200
    mock_requests.get.return_value = mock_resp

    mock_task_requests = mocker.patch('coordinator.tasks.requests')
    mock_task_action = mock.Mock()
    mock_task_action.status_code = 200
    mock_task_action.json.return_value = {'state': 'running'}
    mock_task_requests.post.return_value = mock_task_action

    # Register a task service
    service = {
        'name': 'test release',
        'url': 'http://ts.com'
    }
    resp = client.post(BASE_URL+'/task-services', data=service)
    assert resp.status_code == 201
    assert TaskService.objects.count() == 1
    task_service = resp.json()

    assert Release.objects.count() == 0
    resp = client.get('http://testserver/releases')
    assert resp.status_code == 200

    # Test health check
    ts = TaskService.objects.first()
    ts.health_check()
    assert mock_requests.get.call_count == 1
    mock_requests.get.assert_called_with('http://ts.com/status')

    # Start release
    release = {
        'name': 'First release',
        'description': 'Testing',
        'studies': 'SD_00000000'
    }
    resp = client.post(BASE_URL+'/releases', data=release)
    assert resp.status_code == 201
    release_id = resp.json()['kf_id']

    # Check that the release was initialized and started
    assert mock_task_requests.post.call_count == 2
    init_args, init_kwargs = mock_task_requests.post.call_args_list[0]
    start_args, start_kwargs = mock_task_requests.post.call_args_list[1]

    assert init_args[0] == 'http://ts.com/tasks'
    assert init_kwargs['json']['release_id'] == release_id
    assert init_kwargs['json']['action'] == 'initialize'

    assert start_args[0] == 'http://ts.com/tasks'
    assert start_kwargs['json']['release_id'] == release_id
    assert start_kwargs['json']['action'] == 'start'

    assert Release.objects.first().state == 'running'
    assert Task.objects.first().state == 'running'
