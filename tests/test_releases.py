import json
import pytest
from coordinator.api.models import Release, Event
from coordinator.api.models.release import next_version


def test_version_bumping(db):
    r = Release()
    r.save()
    assert str(r.version) == '0.0.0'
    assert str(next_version()) == '0.0.1'
    assert str(next_version(major=True)) == '1.0.0'
    assert str(next_version(minor=True)) == '0.1.0'
    assert str(next_version(patch=True)) == '0.0.1'


def test_no_releases(client, transactional_db):
    """ Test basic response """
    assert Release.objects.count() == 0
    resp = client.get('http://testserver/releases')
    assert resp.status_code == 200


def test_new_release(admin_client, transactional_db, studies):
    """ Test that new releases may be made """
    assert Release.objects.count() == 0

    release = {
        'name': 'My Release',
        'studies': ['SD_00000001'],
        'author': 'bob'
    }
    resp = admin_client.post('http://testserver/releases', data=release)

    assert resp.status_code == 201
    assert Release.objects.count() == 1
    res = resp.json()
    assert res['kf_id'].startswith('RE_')
    assert len(res['kf_id']) == 11
    assert res['author'] == 'bob'
    assert res['tags'] == []
    assert res['studies'] == ['SD_00000001']
    assert res['version'] == '0.0.0'


def test_patch_bump(admin_client, transactional_db, studies):
    assert Release.objects.count() == 0

    release = {
        'name': 'First Release',
        'studies': ['SD_00000001'],
        'author': 'bob'
    }
    resp = admin_client.post('http://testserver/releases', data=release)
    assert Release.objects.count() == 1
    res = resp.json()
    assert res['version'] == '0.0.0'

    release = {
        'name': 'Second Release',
        'studies': ['SD_00000001'],
        'author': 'bob'
    }
    resp = admin_client.post('http://testserver/releases', data=release)
    assert Release.objects.count() == 2
    res = resp.json()
    assert res['version'] == '0.0.1'

    resp = admin_client.get('http://testserver/releases')
    res = resp.json()
    assert len(res['results']) == 2
    assert res['results'][0]['version'] == '0.0.1'
    assert res['results'][1]['version'] == '0.0.0'


def test_minor_bump(admin_client, transactional_db, studies, worker):
    """ Test that the minor version number is bumped upon publish """
    release = {
        'name': 'First Release',
        'studies': ['SD_00000001'],
        'author': 'bob'
    }
    resp = admin_client.post('http://testserver/releases', data=release)
    assert Release.objects.count() == 1
    res = resp.json()
    assert res['version'] == '0.0.0'

    worker.work(burst=True)

    resp = admin_client.get('http://testserver/releases/'+res['kf_id'])
    res = resp.json()

    resp = admin_client.post('http://testserver/releases/' +
                             res['kf_id']+'/publish')
    worker.work(burst=True)

    resp = admin_client.get('http://testserver/releases/'+res['kf_id'])
    res = resp.json()

    assert res['version'] == '0.1.0'
    assert str(Release.objects.first().version) == '0.1.0'


def test_minor_bump(admin_client, transactional_db, studies, worker):
    """ Test that the major version number is bumped upon publish """
    release = {
        'name': 'First Release',
        'studies': ['SD_00000001'],
        'author': 'bob',
        'is_major': True,
    }
    resp = admin_client.post('http://testserver/releases', data=release)
    assert Release.objects.count() == 1
    res = resp.json()
    assert res['version'] == '0.0.0'

    worker.work(burst=True)

    resp = admin_client.get('http://testserver/releases/'+res['kf_id'])
    res = resp.json()

    resp = admin_client.post('http://testserver/releases/' +
                             res['kf_id']+'/publish')
    worker.work(burst=True)

    resp = admin_client.get('http://testserver/releases/'+res['kf_id'])
    res = resp.json()

    assert res['version'] == '1.0.0'
    assert str(Release.objects.first().version) == '1.0.0'


def test_version_readonly(admin_client, studies):
    """ Test that the user may not assign the version """
    release = {
        'name': 'First Release',
        'studies': ['SD_00000001'],
        'version': '1.1.1',
    }
    resp = admin_client.post('http://testserver/releases', data=release)
    res = resp.json()
    assert res['version'] == '0.0.0'


def test_new_tag(admin_client, transactional_db, study):
    """ Test that tags are updated correctly """
    assert Release.objects.count() == 0

    release = {
            'name': 'My Release',
            'studies': ['SD_00000001']
            }
    resp = admin_client.post('http://testserver/releases', data=release)

    assert resp.status_code == 201
    assert Release.objects.count() == 1
    assert resp.json()['tags'] == []

    kf_id = resp.json()['kf_id']
    tags = {'tags': ['Needs Review', 'Data Fix'], 'studies': ['SD_00000001']}
    resp = admin_client.patch('http://testserver/releases/'+kf_id,
                              data=json.dumps(tags),
                              content_type='application/json')
    assert resp.status_code == 200
    assert resp.json()['tags'] == tags['tags']


def test_get_release_by_id(client, transactional_db, release):
    """ Test that releases may be retrieved by id """
    assert release['kf_id'].startswith('RE_')
    assert len(release['kf_id']) == 11

    resp = client.get('http://testserver/releases/'+release['kf_id'])

    assert resp.status_code == 200
    assert Release.objects.count() == 1
    assert resp.json()['kf_id'].startswith('RE_')
    assert len(resp.json()['kf_id']) == 11


def test_cancel_release(admin_client, transactional_db, release, worker):
    """ Test that a release is canceled and not deleted """
    kf_id = release['kf_id']
    assert Release.objects.count() == 1
    resp = admin_client.delete('http://testserver/releases/'+kf_id)
    worker.work(burst=True)
    assert Release.objects.count() == 1
    res = resp.json()
    assert res['state'] == 'canceling'
    resp = admin_client.get('http://testserver/releases/'+kf_id)
    res = resp.json()
    assert res['state'] == 'canceled'

    # Make sure that we don't re-cancel the release
    assert Event.objects.count() == 2
    resp = admin_client.delete('http://testserver/releases/'+kf_id)
    assert Event.objects.count() == 2


def test_cancel_release_404(admin_client, transactional_db, release):
    """ Test that a release is canceled and not deleted """
    kf_id = release['kf_id']
    assert Release.objects.count() == 1
    resp = admin_client.delete('http://testserver/releases/RE_00000000')
    assert Release.objects.count() == 1
    res = resp.json()

    resp = admin_client.get('http://testserver/releases/'+kf_id)
    res = resp.json()
    assert res['state'] == 'waiting'


def test_study_validator(admin_client, transactional_db):
    """ Test that only correctly formatted study ids are accepted """
    release = {
        'name': 'My Release',
        'studies': ['SD_000', 'SD_00000000'],
    }
    resp = admin_client.post('http://testserver/releases', data=release)
    assert resp.status_code == 400
    res = resp.json()
    assert 'studies' in res
    assert len(res['studies']) == 1
    assert res['studies'][0] == 'Invalid pk "SD_000" - object does not exist.'

    release = {
        'name': 'Release 1',
        'studies': [],
    }
    resp = admin_client.post('http://testserver/releases', data=release)
    assert resp.status_code == 400
    res = resp.json()
    assert 'studies' in res
    assert len(res['studies']) == 1
    assert 'Must have at least one study' in res['studies'][0]


def test_release_relations(client, transactional_db, task):
    resp = client.get('http://testserver/releases')
    res = resp.json()['results'][0]
    assert 'tasks' in res
    assert len(res['tasks']) == 1
    assert 'kf_id' in res['tasks'][0]
    assert res['tasks'][0]['progress'] == 0
