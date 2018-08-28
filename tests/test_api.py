import random
import importlib
import pytest
from mock import Mock, patch
from django.conf import settings


BASE_URL = 'http://testserver'
URLS = [
    '/releases',
    '/task-services',
    '/tasks',
    '/studies',
]


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
