import pytest
from mock import Mock, patch
from coordinator.api.models import Release, TaskService


BASE_URL = 'http://testserver'


@pytest.yield_fixture
def release(client, transactional_db):
    """ Creates a release """
    release = {
        'name': 'test release',
        'studies': ['SD_00000001']
    }
    resp = client.post('http://testserver/releases', data=release)
    return resp.json()


@pytest.yield_fixture
def task_service(client, transactional_db):
    service = {
        'name': 'test service',
        'url': 'http://ts.com',
        'description': 'lorem ipsum',
        'enabled': True
    }
    with patch('coordinator.api.validators.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.content = str.encode('{"name": "test"}')
        mock_resp.status_code = 200
        mock_requests.get.return_value = mock_resp
        resp = client.post(BASE_URL+'/task-services', data=service)
    return resp.json()


@pytest.yield_fixture
def task(client, transactional_db, release, task_service):
    task = {
        'state': 'pending',
        'task_service': BASE_URL+'/task-services/'+task_service['kf_id'],
        'release': BASE_URL+'/releases/'+release['kf_id']
    }
    resp = client.post(BASE_URL+'/tasks', data=task)
    return resp.json()


@pytest.yield_fixture
def event(client, transactional_db, release, task_service, task):
    """ Creates an event """
    event = {
        'event_type': 'info',
        'message': 'New task started for release',
        'release': BASE_URL+'/releases/'+release['kf_id'],
        'task_service': BASE_URL+'/task-services/'+task_service['kf_id'],
        'task': BASE_URL+'/tasks/'+task['kf_id']
    }
    resp = client.post(BASE_URL+'/events', event)
    return resp.json()
