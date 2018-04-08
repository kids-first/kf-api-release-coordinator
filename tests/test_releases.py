import pytest
from rest_framework.test import APIRequestFactory, RequestsClient
from coordinator.api.models import Release


@pytest.yield_fixture
def release(client, transactional_db):
    release = {
	'studies': ['ST_00000001'],
    }
    resp = client.post('http://testserver/releases', data=release)
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
	'studies': ['ST_00000001']
    }
    resp = client.post('http://testserver/releases', data=release)

    assert resp.status_code == 201
    assert Release.objects.count() == 1
    assert resp.json()['kf_id'].startswith('RE_')
    assert len(resp.json()['kf_id']) == 11
    assert resp.json()['studies'] == ['ST_00000001']


def test_get_release_by_id(client, transactional_db, release):
    """ Test that releases may be retrieved by id """
    assert release['kf_id'].startswith('RE_')
    assert len(release['kf_id']) == 11

    resp = client.get('http://testserver/releases/'+release['kf_id'])

    assert resp.status_code == 200
    assert Release.objects.count() == 1
    assert resp.json()['kf_id'].startswith('RE_')
    assert len(resp.json()['kf_id']) == 11


def test_study_validator(client, transactional_db):
    """ Test that only correctly formatted study ids are accepted """
    release = {
	'studies': ['ST_000'],
    }
    resp = client.post('http://testserver/releases', data=release)
    assert resp.status_code == 400
    assert 'studies' in resp.json()
    assert '0' in resp.json()['studies']
    assert resp.json()['studies']['0'] == ['ST_000 is not a valid study kf_id']

    release = {
	'studies': [],
    }
    resp = client.post('http://testserver/releases', data=release)
    assert resp.status_code == 400
    assert 'studies' in resp.json()
    assert 'Ensure this field has at least 1' in resp.json()['studies'][0]
