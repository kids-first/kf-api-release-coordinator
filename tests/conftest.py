import os
import pytest
import random
import django_rq
from mock import Mock, patch
from coordinator.api.models import Release, TaskService
from rest_framework.test import APIClient


BASE_URL = 'http://testserver'

with open(os.path.join(os.path.dirname(__file__), 'admin_token.txt')) as f:
    ADMIN_TOKEN = f.read().strip()
with open(os.path.join(os.path.dirname(__file__), 'user_token.txt')) as f:
    USER_TOKEN = f.read().strip()


@pytest.yield_fixture(autouse=True)
def mock_ego(mocker):
    mock_auth_requests = mocker.patch('coordinator.authentication.requests')
    mock_auth_resp = Mock()
    mock_auth_resp.status_code = 200
    mock_auth_resp.json.return_value = True
    mock_auth_requests.get.return_value = mock_auth_resp


@pytest.yield_fixture
def admin_client():
    """ Injects admin JWT into each request """
    client = APIClient()
    client.credentials(headers={'Authorization': 'Bearer ' + ADMIN_TOKEN})
    yield client


@pytest.yield_fixture
def worker():
    worker = django_rq.get_worker()
    return worker


@pytest.yield_fixture
def release(admin_client, transactional_db):
    """ Creates a release """
    release = {
        'name': 'test release',
        'studies': ['SD_00000001']
    }
    resp = admin_client.post('http://testserver/releases', data=release)
    return resp.json()


@pytest.yield_fixture
def task_service(admin_client, transactional_db):
    service = {
        'name': 'test service',
        'url': 'http://ts.com',
        'author': 'daniel@d3b.center',
        'description': 'lorem ipsum',
        'enabled': True
    }
    with patch('coordinator.api.validators.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.content = str.encode('{"name": "test"}')
        mock_resp.status_code = 200
        mock_requests.get.return_value = mock_resp
        resp = admin_client.post(BASE_URL+'/task-services', data=service)
    return resp.json()


@pytest.yield_fixture
def task(admin_client, transactional_db, release, task_service):
    task = {
        'state': 'pending',
        'task_service': BASE_URL+'/task-services/'+task_service['kf_id'],
        'release': BASE_URL+'/releases/'+release['kf_id']
    }
    resp = admin_client.post(BASE_URL+'/tasks', data=task)
    return resp.json()


@pytest.yield_fixture
def event(admin_client, transactional_db, release, task_service, task):
    """ Creates an event """
    event = {
        'event_type': 'info',
        'message': 'task {} has changed from {} to {}'
                   .format(task['kf_id'], 'waiting', 'initializing'),
        'release': BASE_URL+'/releases/'+release['kf_id'],
        'task_service': BASE_URL+'/task-services/'+task_service['kf_id'],
        'task': BASE_URL+'/tasks/'+task['kf_id']
    }
    resp = admin_client.post(BASE_URL+'/events', event)
    return resp.json()


@pytest.yield_fixture
def releases(admin_client):
    rel = {}
    for i in range(5):
        r = admin_client.post(BASE_URL+'/releases',
                              {'name': 'TEST',
                               'studies': 'SD_{0:08d}'.format(i)})
        rel[r.json()['kf_id']] = r.json()
    return rel


@pytest.yield_fixture
def task_services(admin_client):
    ts = {}
    with patch('coordinator.api.validators.requests') as mock_requests:
        mock_resp = Mock()
        mock_resp.content = str.encode('{"name": "test"}')
        mock_resp.status_code = 200
        mock_requests.get.return_value = mock_resp

        for i in range(10):
            r = admin_client.post(BASE_URL+'/task-services',
                                  {'name': 'TASK SERVICE {}'.format(i),
                                   'url': 'http://localhost',
                                   'author': 'daniel@d3b.center',
                                   'description': 'test'})
            ts[r.json()['kf_id']] = r.json()
    return ts


@pytest.yield_fixture
def tasks(admin_client, releases, task_services):
    ta = {}
    for i in range(50):
        rel = releases[random.choice(list(releases.keys()))]['kf_id']
        ts = task_services[random.choice(list(task_services.keys()))]['kf_id']
        r = admin_client.post(BASE_URL+'/tasks',
                              {'name': 'TASK {}'.format(i),
                               'release': BASE_URL+'/releases/'+rel,
                               'task_service': BASE_URL+'/task-services/'+ts})
        ta[r.json()['kf_id']] = r.json()
    return ta


@pytest.yield_fixture
def fakes(releases, task_services, tasks):
    return {'releases': releases,
            'task-services': task_services,
            'tasks': tasks}
