import pytest
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
        'name': 'test release',
        'url': 'http://ts.com'
    }
    resp = client.post(BASE_URL+'/task-services', data=service)
    return resp.json()
