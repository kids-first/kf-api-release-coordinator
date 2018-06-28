import pytest
from requests.exceptions import ConnectionError
from mock import Mock, patch
from coordinator.api.models import TaskService, Task


BASE_URL = 'http://testserver'


def test_no_task_service(client, transactional_db):
    """ Test basic response """
    assert TaskService.objects.count() == 0
    resp = client.get(BASE_URL+'/task-services')
    assert resp.status_code == 200


def test_basic_task_service(client, transactional_db, task_service):
    """ Test basic response """
    assert TaskService.objects.count() == 1
    resp = client.get(BASE_URL+'/task-services')
    assert resp.status_code == 200
    res = resp.json()
    assert res['count'] == 1


def test_url_validation(admin_client, db, task_service):
    """ Test that urls are validated by pinging their status endpoint """
    orig = TaskService.objects.count()
    with patch('coordinator.api.validators.requests') as mock_requests:
        mock_requests.get = Mock()
        mock_resp = Mock()
        mock_resp.content = str.encode('')
        mock_requests.get.return_value = mock_resp
        mock_requests.get.status_code.return_value = 404

        # Test basic url field validation
        service = {'url': 'not a url',
                   'name': 'test service',
                   'author': 'daniel@d3b.center',
                   'description': 'lorem ipsum'}
        resp = admin_client.post(BASE_URL+'/task-services', data=service)
        res = resp.json()
        assert res['url'][0] == 'Enter a valid URL.'
        assert TaskService.objects.count() == orig

        # Test validation against endpoint

        service['url'] = 'http://validurl.com'
        resp = admin_client.post(BASE_URL+'/task-services', data=service)
        res = resp.json()
        assert 'validurl.com did not return the expected /st' in res['url'][0]
        assert TaskService.objects.count() == orig

        mock_resp.status_code = 200
        mock_resp.content = str.encode('{}')
        mock_requests.get.return_value = mock_resp
        resp = admin_client.post(BASE_URL+'/task-services', data=service)
        res = resp.json()
        assert 'validurl.com did not return the expected /st' in res['url'][0]
        assert TaskService.objects.count() == orig

        mock_resp.content = str.encode('{"name": "test"}')
        mock_requests.get.return_value = mock_resp
        resp = admin_client.post(BASE_URL+'/task-services', data=service)
        res = resp.json()
        assert 'kf_id' in res
        assert TaskService.objects.count() == orig + 1


def test_no_author(admin_client, db, task_service, mocker):
    """ Check that author default to the token's user's name """
    mock_service_requests = mocker.patch('coordinator.api.validators.requests')
    mock_service_resp = Mock()
    mock_service_resp.status_code = 200
    mock_service_resp.content = str.encode('{"name": "test"}')
    mock_service_requests.get.return_value = mock_service_resp

    # Register a task service
    service = {
        'name': 'test release',
        'url': 'http://task',
        'author': 'daniel@d3b.center',
        'description': 'lorem ipsum',
        'enabled': True
    }
    resp = admin_client.post(BASE_URL+'/task-services', data=service)
    assert resp.status_code == 201
    new_task_service = resp.json()
    obj = TaskService.objects.get(kf_id=new_task_service['kf_id'])
    assert obj.author == 'daniel@d3b.center'


def test_disabled_task(admin_client, db, task_service, mocker):
    orig = TaskService.objects.count()

    mock_service_requests = mocker.patch('coordinator.api.validators.requests')
    mock_service_resp = Mock()
    mock_service_resp.status_code = 200
    mock_service_resp.content = str.encode('{"name": "test"}')
    mock_service_requests.get.return_value = mock_service_resp

    # Register a task service
    service = {
        'name': 'test release',
        'url': 'http://task',
        'author': 'daniel@d3b.center',
        'description': 'lorem ipsum',
        'enabled': True
    }
    resp = admin_client.post(BASE_URL+'/task-services', data=service)
    assert resp.status_code == 201
    assert TaskService.objects.count() == orig + 1
    new_task_service = resp.json()
    # Disable task service
    url = BASE_URL+'/task-services/'+new_task_service['kf_id']
    resp = admin_client.patch(url,
                              data='{"enabled": false}',
                              content_type='application/json')
    assert resp.status_code == 200
    assert not TaskService.objects.get(kf_id=new_task_service['kf_id']).enabled

    # Run release
    mock_requests = mocker.patch('coordinator.api.models.requests')
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_requests.get.return_value = mock_resp

    mock_tasks_requests = mocker.patch('coordinator.tasks.requests')
    mock_task_resp = Mock()
    mock_task_resp.status_code = 200
    mock_task_resp.json.return_value = {'state': 'pending'}
    mock_tasks_requests.post.return_value = mock_task_resp

    release = {
        'name': 'v1', 'description': 'Testing', 'studies': 'SD_00000000'
    }
    resp = admin_client.post(BASE_URL+'/releases', data=release)
    # Check that the disabled service was never called
    ta = TaskService.objects.get(kf_id=task_service['kf_id'])
    ta = TaskService.objects.get(kf_id=task_service['kf_id']).tasks.all()[0]
    expected = {
        'action': 'initialize',
        'task_id': ta.kf_id,
        'release_id': ta.release.kf_id
    }
    mock_tasks_requests.post.assert_any_call('http://ts.com/tasks',
                                             json=expected)
    for call in mock_tasks_requests.post.call_args_list:
        assert 'http://task/' not in call[0]


@pytest.mark.parametrize('field', [
    'kf_id',
    'url',
    'author',
    'health_status',
    'last_ok_status',
    'enabled',
    'created_at'
])
def test_task_service_fields(client, db, task_service, field):
    resp = client.get(BASE_URL+'/task-services')
    task_service = resp.json()['results'][0]
    assert field in task_service


@pytest.mark.parametrize('field', [
    'tasks',
])
def test_task_service_non_fields(client, db, task_service, field):
    resp = client.get(BASE_URL+'/task-services')
    task_service = resp.json()['results'][0]
    assert field not in task_service


def test_task_service_bad_status(client, db, task_service):
    """ Test that a non-200 response increases task's last_ok_status count """
    kf_id = task_service['kf_id']
    ts = TaskService.objects.get(kf_id=kf_id)
    with patch('coordinator.api.models.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = ConnectionError()
        mock_requests.get.return_value = mock_resp
        mock_requests.get.status_code.return_value = 404
        ts.health_check()
        assert mock_requests.get.call_count == 1
        assert ts.health_status == 'ok'
        mock_requests.get.assert_called_with('http://ts.com/status')
        assert ts.last_ok_status == 1
        ts.health_check()
        ts.health_check()
        ts.health_check()
        assert ts.last_ok_status == 4
        assert ts.health_status == 'down'
