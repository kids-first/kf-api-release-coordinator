import pytest
from rest_framework.test import APIRequestFactory, RequestsClient
from coordinator.api.models import Release


@pytest.yield_fixture
def release(client, transactional_db):
    release = {
	'studies': ['ST_00000001'],
    }
    resp = client.post('http://testserver/releases', json=release)
    return resp.json()


def test_no_releases(client, transactional_db):
    """ Test basic response """
    assert Release.objects.count() == 0
    resp = client.get('http://testserver/releases')
    assert resp.status_code == 200


def test_new_release(client, transactional_db):
    """ Test that new releases may be made """
    assert Release.objects.count() == 0

    release = {
	'studies': ['ST_00000001'],
    }
    resp = client.post('http://testserver/releases', json=release)

    assert resp.status_code == 201
    assert Release.objects.count() == 1


def test_get_release_by_id(client, transactional_db, release):
    resp = client.get('http://testserver/releases/'+release['kf_id'])

    assert resp.status_code == 200
    assert Release.objects.count() == 1
