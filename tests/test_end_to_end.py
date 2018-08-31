import os
import json
import pytest
import mock
from coordinator.api.models import Release, Task, TaskService, Event


BASE_URL = 'http://testserver'

with open(os.path.join(os.path.dirname(__file__), 'dev_token.txt')) as f:
    DEV_TOKEN = f.read().strip()


def test_full_release(client, transactional_db, mocker, worker, study):
    """
    Test a full release:
    1) Create task service
    2) Create release
    """
    mock_task_requests = mocker.patch('coordinator.tasks.requests')
    mock_task_action = mock.Mock()
    mock_task_action.status_code = 200
    mock_task_action.json.return_value = {'state': 'running'}
    mock_task_requests.post.return_value = mock_task_action

    mock_service_requests = mocker.patch('coordinator.api.validators.requests')
    mock_service_resp = mock.Mock()
    mock_service_resp.status_code = 200
    mock_service_resp.content = str.encode('{"name": "test"}')
    mock_service_requests.get.return_value = mock_service_resp

    # Register a task service
    service = {
        'name': 'test service',
        'url': 'http://ts.com',
        'author': 'daniel@d3b.center',
        'description': 'lorem ipsum',
        'enabled': True
    }
    resp = client.post(BASE_URL+'/task-services',
                       data=service,
                       headers={'Authorization': 'Bearer '+DEV_TOKEN})
    assert resp.status_code == 201
    assert TaskService.objects.count() == 1
    task_service = resp.json()

    assert Release.objects.count() == 0
    resp = client.get('http://testserver/releases')
    assert resp.status_code == 200

    mock_requests = mocker.patch('coordinator.api.models.taskservice.requests')
    mock_resp = mock.Mock()
    mock_resp.status_code = 200
    mock_requests.get.return_value = mock_resp

    # Test health check
    ts = TaskService.objects.first()
    ts.health_check()
    assert mock_requests.get.call_count == 1
    mock_requests.get.assert_called_with('http://ts.com/status', timeout=0.1)

    # Start release
    release = {
        'name': 'First release',
        'description': 'Testing',
        'studies': ['SD_00000001'],
        'tags': []
    }
    resp = client.post(BASE_URL+'/releases',
                       data=release,
                       headers={'Authorization': 'Bearer '+DEV_TOKEN})

    assert resp.status_code == 201
    release_id = resp.json()['kf_id']

    # Now have the rq worker do it's work
    worker.work(burst=True)

    # Check that the task was initialized and started
    # NB: We cannot inspect the mock as the calls were made in a fork
    # assert mock_task_requests.post.call_count == 2
    # init_args, init_kwargs = mock_task_requests.post.call_args_list[0]
    # start_args, start_kwargs = mock_task_requests.post.call_args_list[1]

    # assert init_args[0] == 'http://ts.com/tasks'
    # assert init_kwargs['json']['release_id'] == release_id
    # assert init_kwargs['json']['action'] == 'initialize'

    # assert start_args[0] == 'http://ts.com/tasks'
    # assert start_kwargs['json']['release_id'] == release_id
    # assert start_kwargs['json']['action'] == 'start'

    assert Release.objects.first().state == 'running'
    assert Task.objects.first().state == 'running'

    resp = client.get(BASE_URL+'/releases/'+release_id)
    assert resp.status_code == 200
    res = resp.json()
    task_id = res['tasks'][0]['kf_id']
    assert len(res['tasks']) == 1
    assert res['tasks'][0]['state'] == 'running'
    assert Task.objects.first().kf_id == task_id

    resp = client.get(BASE_URL+'/tasks/'+task_id)
    assert resp.status_code == 200
    res = resp.json()
    assert res['state'] == 'running'
    assert res['progress'] == 0
    assert res['release'] == BASE_URL+'/releases/'+release_id

    # Send back a response to the coordinator mocking the task
    resp = client.patch(BASE_URL+'/tasks/'+task_id,
                        json.dumps({'progress': 50}),
                        content_type='application/json')
    assert resp.status_code == 200
    res = resp.json()
    assert res['state'] == 'running'
    assert res['progress'] == 50

    # Tell the coordinator the task has been staged
    # Send back a response to the coordinator mocking the task
    resp = client.patch(BASE_URL+'/tasks/'+task_id,
                        json.dumps({'state': 'staged', 'progress': 100}),
                        content_type='application/json')

    assert resp.status_code == 200
    res = resp.json()
    assert res['state'] == 'staged'
    assert res['progress'] == 100

    resp = client.get(BASE_URL+'/releases/'+release_id)
    assert resp.status_code == 200
    res = resp.json()
    assert res['state'] == 'staged'
    assert all([t['state'] == 'staged' for t in res['tasks']])

    # Send publish command
    mock_task_action.json.return_value = {'state': 'publishing'}

    resp = client.post(BASE_URL+'/releases/'+release_id+'/publish',
                       headers={'Authorization': 'Bearer '+DEV_TOKEN})
    assert resp.status_code == 200
    res = resp.json()
    assert res['message'] == 'publishing'

    worker.work(burst=True)

    # Mock a task's response telling the coordinator it has published
    resp = client.patch(BASE_URL+'/tasks/'+task_id,
                        json.dumps({'state': 'published', 'progress': 100}),
                        content_type='application/json')
    assert resp.status_code == 200
    res = resp.json()
    assert res['state'] == 'published'

    resp = client.get(BASE_URL+'/releases/'+release_id)
    assert resp.status_code == 200
    res = resp.json()
    assert res['state'] == 'published'
    assert all([t['state'] == 'published' for t in res['tasks']])
