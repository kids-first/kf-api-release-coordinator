import json
import pytest
from rest_framework.test import APIRequestFactory, RequestsClient
from coordinator.api.models import Release


@pytest.yield_fixture
def release(client, transactional_db):
    release = {
        'name': 'test release',
	'studies': ['ST_00000001']
    }
    resp = client.post('http://testserver/releases', data=release)
    return resp.json()['results']


def test_no_releases(client, transactional_db):
    """ Test basic response """
    assert Release.objects.count() == 0
    resp = client.get('http://testserver/releases')
    assert resp.status_code == 200


def test_new_release(client, transactional_db):
    """ Test that new releases may be made """
    assert Release.objects.count() == 0

    release = {
        'name': 'My Release',
	'studies': ['ST_00000001']
    }
    resp = client.post('http://testserver/releases', data=release)

    assert resp.status_code == 201
    assert Release.objects.count() == 1
    res = resp.json()['results']
    assert res['kf_id'].startswith('RE_')
    assert len(res['kf_id']) == 11
    assert res['author'] == 'admin'
    assert res['tags'] == []
    assert res['studies'] == ['ST_00000001']


def test_new_tag(client, transactional_db):
    """ Test that tags are updated correctly """
    assert Release.objects.count() == 0

    release = {
        'name': 'My Release',
	'studies': ['ST_00000001']
    }
    resp = client.post('http://testserver/releases', data=release)

    assert resp.status_code == 201
    assert Release.objects.count() == 1
    assert resp.json()['results']['tags'] == []

    kf_id = resp.json()['results']['kf_id']
    tags = {'tags': ['Needs Review', 'Data Fix'], 'studies': ['ST_00000001']}
    resp = client.patch('http://testserver/releases/'+kf_id,
                        data=json.dumps(tags),
                        content_type='application/json')
    assert resp.status_code == 200
    assert resp.json()['results']['tags'] == tags['tags']


def test_get_release_by_id(client, transactional_db, release):
    """ Test that releases may be retrieved by id """
    assert release['kf_id'].startswith('RE_')
    assert len(release['kf_id']) == 11

    resp = client.get('http://testserver/releases/'+release['kf_id'])

    assert resp.status_code == 200
    assert Release.objects.count() == 1
    assert resp.json()['results']['kf_id'].startswith('RE_')
    assert len(resp.json()['results']['kf_id']) == 11


def test_study_validator(client, transactional_db):
    """ Test that only correctly formatted study ids are accepted """
    release = {
        'name': 'My Release',
	'studies': ['ST_000', 'ST_00000000'],
    }
    resp = client.post('http://testserver/releases', data=release)
    assert resp.status_code == 400
    res = resp.json()['results']
    assert 'studies' in res
    assert len(res['studies']) == 1
    assert res['studies']['0'] == ['ST_000 is not a valid study kf_id']

    release = {
	'studies': [],
    }
    resp = client.post('http://testserver/releases', data=release)
    assert resp.status_code == 400
    res = resp.json()['results']
    assert 'studies' in res
    assert len(res['studies']) == 1
    assert 'Ensure this field has at least 1' in res['studies'][0]
