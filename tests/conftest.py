import os
import pytest
import random
import django_rq
from datetime import datetime, timezone, timedelta
from mock import Mock, patch
from coordinator.api.models import Release, TaskService, Study, Task
from rest_framework.test import APIClient
from unittest import mock
import jwt


BASE_URL = 'http://testserver'


@pytest.yield_fixture(scope='session', autouse=True)
def ego_key_mock():
    """
    Mocks out the response from the /oauth/token/public_key endpoint
    """
    auth = 'coordinator.authentication.EgoAuthentication'
    with mock.patch(f'{auth}._get_new_key') as get_key:
        with open('tests/keys/public_key.pem', 'rb') as f:
            get_key.return_value = f.read()
            yield get_key


@pytest.yield_fixture(autouse=True)
def mock_ego(mocker):
    """
    Mocks requests to ego

    POST requests are assumed to go to /oauth/token and will respond
      with a new access_token
    """
    mock_auth_requests = mocker.patch(
        'coordinator.authentication.requests.post'
    )
    mock_post_resp = Mock()
    mock_post_resp.status_code = 200
    mock_post_resp.json.return_value = {
        'access_token': 'abc',
        'expires_in': 1000
    }
    mock_auth_requests.return_value = mock_post_resp


@pytest.yield_fixture
def client():
    """ Sets client to use json requests """
    client = APIClient(content_type='json')
    yield client


@pytest.yield_fixture
def admin_client(token):
    """ Injects admin JWT into each request """
    client = APIClient(content_type='json')
    client.credentials(
        headers={'Authorization': 'Bearer '+token(roles=['ADMIN'])}
    )
    yield client


@pytest.yield_fixture
def dev_client(token):
    """ Injects dev JWT into each request """
    client = APIClient(content_type='json')
    client.credentials(
        headers={'Authorization': 'Bearer '+token(roles=['DEV'],
                 groups=['SD_00000001'])}
    )
    yield client


@pytest.yield_fixture
def user_client(token):
    """ Injects user JWT into each request """
    client = APIClient(content_type='json')
    client.credentials(
        headers={'Authorization': 'Bearer '+token(groups=['SD_00000001'])}
    )
    yield client


@pytest.yield_fixture
def test_client(admin_client, dev_client, user_client, client):
    """ Returns a client for the specified user_type """
    yield lambda user_type: {
        "admin": admin_client,
        "dev": dev_client,
        "user": user_client,
        "anon": client,
    }[user_type]


@pytest.yield_fixture
def worker():
    # Clear queue
    q = django_rq.get_queue()
    q.empty()

    worker = django_rq.get_worker()
    return worker


@pytest.yield_fixture
def release(admin_client, transactional_db, study):
    """ Creates a release """
    release = {
        'name': 'test release',
        'studies': ['SD_00000001'],
        'tags': [],
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
def study(admin_client, transactional_db):
    study = {
        'kf_id': 'SD_00000001',
        'name': 'Test Study',
        'visible': True,
    }
    # Study cannot be created through api, so it must be made with ORM
    study = Study(**study)
    study.save()
    return study


@pytest.yield_fixture
def release_note(admin_client, transactional_db, release, study):
    note = {
        'kf_id': 'RN_00000001',
        'description': 'Lorem ipsum',
        'release': BASE_URL+'/releases/'+release['kf_id'],
        'study': BASE_URL+'/studies/'+study.kf_id
    }
    resp = admin_client.post(BASE_URL+'/release-notes', data=note)
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
def studies(transactional_db):
    sd = {}
    for i in range(5):
        study = {'name': f'Study {i}',
                 'kf_id': 'SD_{0:08d}'.format(i),
                 'visible': True,
                 'created_at': datetime(year=2000, month=1, day=5,
                                        tzinfo=timezone.utc)}
        sd[study['kf_id']] = Study(**study)
        sd[study['kf_id']].save()
    return sd


@pytest.yield_fixture
def releases(admin_client, studies):
    rel = {}
    for i in range(5):
        r = Release(name='TEST')
        r.save()
        r.studies.set([list(studies.values())[i]])
        rel[r.kf_id] = r
        r.save()
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
            t = {'name': 'TASK SERVICE {}'.format(i),
                 'url': 'http://localhost',
                 'author': 'daniel@d3b.center',
                 'description': 'test'}
            t = TaskService(**t)
            ts[t.kf_id] = t
    TaskService.objects.bulk_create(ts.values())
    return ts


@pytest.yield_fixture
def tasks(admin_client, releases, task_services):
    ta = {}
    for i in range(50):
        rel = releases[random.choice(list(releases.keys()))]
        ts = task_services[random.choice(list(task_services.keys()))]
        t = Task(release=rel, task_service=ts)
        ta[t.kf_id] = t
    Task.objects.bulk_create(ta.values())
    return ta


@pytest.yield_fixture
def fakes(releases, task_services, tasks):
    return {'releases': releases,
            'task-services': task_services,
            'tasks': tasks}


@pytest.yield_fixture
def token():
    """
    Returns a function that will generate a token for a user in given groups
    with given roles.
    """
    with open('tests/keys/private_key.pem', 'rb') as f:
        ego_key = f.read()

    def make_token(groups=None, roles=None):
        """
        Returns an ego JWT for a user with given roles and groups
        """
        if groups is None:
            groups = []
        if roles is None:
            roles = ['USER']

        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        token = {
          "iat": now.timestamp(),
          "exp": tomorrow.timestamp(),
          "sub": "cfa211bc-6fa8-4a03-bb81-cf377f99da47",
          "iss": "ego",
          "aud": "creator",
          "jti": "7b42a89d-85e3-4954-81a0-beccb12f32d5",
          "context": {
            "user": {
              "name": "user@d3b.center",
              "email": "user@d3b.center",
              "status": "Approved",
              "firstName": "Bobby",
              "lastName": "TABLES;",
              "createdAt": 1531440000000,
              "lastLogin": 1551293729279,
              "preferredLanguage": None,
              "groups": groups,
              "roles": roles,
              "permissions": []
            }
          }
        }

        return jwt.encode(token, ego_key, algorithm='RS256').decode('utf8')
    return make_token


@pytest.yield_fixture
def user_headers(token):
    """
    Returning headers for given user type
    """
    def get_header(user_type):
        return {
            'admin_user': {'Authorization': 'Bearer '+token(roles=['ADMIN'])},
            'dev_user': {'Authorization': 'Bearer '+token(roles=['DEV'])},
            'user': {'Authorization': 'Bearer '+token()},
            'unauthed_user': {}
        }[user_type]
    return get_header
