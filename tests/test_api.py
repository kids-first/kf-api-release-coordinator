import random
import importlib
import pytest
from django.conf import settings


BASE_URL = 'http://testserver'
URLS = [
    '/releases',
    '/task-services',
    '/tasks',
]


@pytest.yield_fixture
def releases(client):
    rel = {}
    for i in range(5):
        r = client.post(BASE_URL+'/releases',
                        {'name': 'TEST', 'studies': 'SD_{0:08d}'.format(i)})
        rel[r.json()['kf_id']] = r.json()
    return rel


@pytest.yield_fixture
def task_services(client):
    ts = {}
    for i in range(10):
        r = client.post(BASE_URL+'/task-services',
                        {'name': 'TASK SERVICE {}'.format(i),
                         'url': 'http://localhost'})
        ts[r.json()['kf_id']] = r.json()
    return ts


@pytest.yield_fixture
def tasks(client, releases, task_services):
    ta = {}
    for i in range(50):
        rel = releases[random.choice(list(releases.keys()))]['kf_id']
        ts = task_services[random.choice(list(task_services.keys()))]['kf_id']
        r = client.post(BASE_URL+'/tasks',
                        {'name': 'TASK {}'.format(i),
                         'release_id': rel,
                         'task_service_id': ts})
        ta[r.json()['kf_id']] = r.json()
    return ta


@pytest.yield_fixture
def fakes(releases, task_services, tasks):
    return {'releases': releases,
            'task-services': task_services,
            'tasks': tasks}


@pytest.mark.parametrize('endpoint', URLS)
@pytest.mark.parametrize('method', ['get', 'post', 'patch', 'put'])
def test_response_codes_200(client, db, endpoint, method):
    call = getattr(client, method)
    r = call(BASE_URL+endpoint)
    r.status_code == 200


@pytest.mark.parametrize('endpoint', URLS)
@pytest.mark.parametrize('method', ['get', 'post', 'patch', 'put', 'delete'])
def test_response_codes_404(client, db, endpoint, method):
    call = getattr(client, method)
    r = call(BASE_URL+endpoint+'/SD_XXXXXXXX')
    r.status_code == 404


@pytest.mark.parametrize('endpoint,count', zip(URLS, [5, 10, 50]))
def test_pagination(client, db, fakes, endpoint, count):
    resp = client.get(endpoint)
    res = resp.json()
    assert 'results' in res
    assert 'next' in res
    assert 'previous' in res
    assert 'count' in res
    assert res['count'] == count
