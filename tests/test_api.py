import importlib
import pytest
from django.conf import settings


URLS = [
    '/releases',
    '/task-services',
    '/tasks',
]

URLS = [ 'http://testserver'+url for url in URLS]


@pytest.mark.parametrize('endpoint', URLS)
def test_envelope(client, transactional_db, endpoint):
    """ Test endpoint for stadard envelope """
    resp = client.get(endpoint)
    r = resp.json()

    assert '_status' in r
    assert 'code' in r['_status']
    assert 'message' in r['_status']
    assert '_links' in r
    assert 'self' in r['_links']
    #assert endpoint in r['_links']['self']
    assert r['_status']['code'] == resp.status_code
